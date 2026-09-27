import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import upgrade

class UpgradeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.instance = self.root / 'instance'
        self.instance.mkdir(mode=0o700)
        self.images = {k: 'sha256:' + 'a'*64 for k in upgrade.manage.SERVICES}
        self.new_images = dict(self.images, api='sha256:'+'b'*64)
        self.compose = {'services': {k: {'image': v} for k,v in self.images.items()}, 'volumes': {}}
        (self.instance/'runtime.json').write_text(json.dumps({'Instance': {'Mode': 'Independent', 'Name': 'Test'}}))
        (self.instance/'compose.json').write_text(json.dumps(self.compose))
        self.manifest = self.root/'release.json'
        self.release = {'format': 'talkrax-independent-update-v1', 'releaseId': 'test-2',
                        'fromImages': self.images, 'images': self.new_images}
        self.records = [{'State': {'Running': True}, 'Image': self.images[k],
                         'Config': {'Labels': {'com.docker.compose.service': k}}} for k in self.images]

    def save(self):
        self.manifest.write_text(json.dumps(self.release))
        return hashlib.sha256(self.manifest.read_bytes()).hexdigest()

    def plan(self, checksum=None):
        with patch.object(upgrade, 'owned_resources', return_value=self.records), \
             patch.object(upgrade, 'output', return_value=json.dumps([{'Id': 'sha256:'+'a'*64}])):
            return upgrade.plan(self.instance, 'talkrax-unit', self.manifest, checksum or self.save())

    def test_plan_and_exact_source_inventory(self):
        self.assertEqual(self.plan()[-1], ['api'])
        self.release['fromImages']['api'] = 'sha256:'+'c'*64
        with self.assertRaisesRegex(ValueError, 'installed image inventory'):
            self.plan()

    def test_changed_dependency_mutable_image_and_tamper_rejected(self):
        for change in ('dependency','mutable','inventory','checksum'):
            with self.subTest(change=change):
                self.release['images'] = self.new_images.copy()
                if change == 'dependency': self.release['images']['postgres'] = 'sha256:'+'f'*64
                if change == 'mutable': self.release['images']['api'] = 'example/api:latest'
                if change == 'inventory': del self.release['images']['admin']
                checksum = self.save()
                if change == 'checksum': checksum = '0'*64
                with self.assertRaises(ValueError): self.plan(checksum)

    def test_pending_recovery_or_changed_running_image_blocks_plan(self):
        for status in ('preparing','starting','recovery-required'):
            upgrade.atomic_json(self.instance/upgrade.STATE, {'status':status})
            with self.assertRaisesRegex(ValueError, 'incomplete update'): self.plan()
        (self.instance/upgrade.STATE).unlink()
        self.records[0]['Image'] = 'sha256:'+'c'*64
        with self.assertRaisesRegex(ValueError, 'Running image'): self.plan()

    def test_project_collision_rejected_before_mutation(self):
        record = {'Config': {'Labels': {'com.docker.compose.project.config_files':'/production/compose.json'}},
                  'State': {'Running':True}}
        with patch.object(upgrade, 'output', side_effect=['abc',json.dumps([record])]):
            with self.assertRaisesRegex(ValueError, 'different installation'):
                upgrade.owned_resources(self.instance, 'talkrax-production')

    def test_redis_anonymous_volume_must_be_exclusive(self):
        records = []
        for name in upgrade.manage.SERVICES:
            records.append({'Id':name+'-container', 'Config': {'Labels': {
                'com.docker.compose.project.config_files':str(self.instance/'compose.json'),
                'com.docker.compose.service':name}}, 'Mounts':[]})
        redis = next(r for r in records if r['Id']=='redis-container')
        redis['Mounts'] = [{'Type':'volume','Name':'f'*64,'Destination':'/data'}]
        for mounted_by, accepted in [('redis-container',True),('redis-container\nforeign-container',False)]:
            with self.subTest(mounted_by=mounted_by), patch.object(upgrade,'output',
                side_effect=['containers',json.dumps(records),mounted_by]):
                if accepted:
                    self.assertEqual(len(upgrade.owned_resources(self.instance,'talkrax-unit')),7)
                else:
                    with self.assertRaisesRegex(ValueError,'Shared volume'):
                        upgrade.owned_resources(self.instance,'talkrax-unit')

    def test_cli_start_cannot_bypass_an_active_operator_lock(self):
        import subprocess
        import sys
        with upgrade.lock(self.instance):
            result = subprocess.run([sys.executable,str(Path(upgrade.manage.__file__)),
                '--directory',str(self.instance),'--project','talkrax-unit','start'],
                capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Another operator operation',result.stderr)

    def test_lock_is_exclusive_and_released_after_exception(self):
        with upgrade.lock(self.instance):
            with self.assertRaisesRegex(ValueError, 'Another operator'):
                with upgrade.lock(self.instance): pass
        with upgrade.lock(self.instance): pass

    def test_failed_candidate_requires_restore_never_starts_old_code(self):
        checksum = self.save()
        commands = []
        plan = (self.instance,['docker','compose'],self.compose,self.release,['api'])
        with patch.object(upgrade,'plan',return_value=plan), \
             patch.object(upgrade,'ensure_images'), \
             patch.object(upgrade.manage,'backup'), \
             patch.object(upgrade.manage,'validate_backup'), \
             patch.object(upgrade.manage,'execute',side_effect=lambda args,**kwargs: commands.append(args)), \
             patch.object(upgrade,'wait_healthy',side_effect=RuntimeError('not healthy')), \
             patch.object(upgrade.subprocess,'run') as run:
            with self.assertRaises(RuntimeError):
                upgrade.apply(self.instance,'talkrax-unit',self.manifest,checksum,self.root/'backup')
            self.assertEqual(upgrade.read_json(self.instance/upgrade.STATE)['status'],'recovery-required')
            self.assertEqual(upgrade.read_json(self.instance/'compose.json')['services']['api']['image'],self.new_images['api'])
            self.assertIn('stop',run.call_args.args[0])
            self.assertEqual(sum('up' in command for command in commands),1)

    def test_failed_backup_resumes_only_original_images(self):
        checksum = self.save()
        plan = (self.instance,['docker','compose'],self.compose,self.release,['api'])
        with patch.object(upgrade,'plan',return_value=plan), \
             patch.object(upgrade,'ensure_images'), \
             patch.object(upgrade.manage,'backup',side_effect=RuntimeError('backup unavailable')), \
             patch.object(upgrade.manage,'execute'), \
             patch.object(upgrade.subprocess,'run') as run:
            run.return_value.returncode = 0
            with self.assertRaises(RuntimeError):
                upgrade.apply(self.instance,'talkrax-unit',self.manifest,checksum,self.root/'backup')
            self.assertEqual(upgrade.read_json(self.instance/'compose.json'),self.compose)
            self.assertEqual(upgrade.read_json(self.instance/upgrade.STATE)['status'],'healthy')
            self.assertIn('up',run.call_args.args[0])

if __name__ == '__main__':
    unittest.main()
