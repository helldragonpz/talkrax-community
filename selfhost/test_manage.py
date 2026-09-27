import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('manage',Path(__file__).with_name('manage.py'))
manage=importlib.util.module_from_spec(spec);spec.loader.exec_module(manage)

class BackupSafetyTests(unittest.TestCase):
 def fixture(self,root,entry='file.txt',kind=None):
  for name in manage.BACKUP_FILES:
   if name!='storage.tar':(root/name).write_text('synthetic fixture')
  with tarfile.open(root/'storage.tar','w:') as archive:
   member=tarfile.TarInfo(entry)
   if kind is not None:
    member.type=kind;member.linkname='/etc/passwd'
   archive.addfile(member)
  files={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in manage.BACKUP_FILES}
  (root/'manifest.json').write_text(json.dumps({'format':'talkrax-independent-backup-v1','files':files}))

 def test_valid_private_backup_and_corrupt_dump(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.fixture(root)
   self.assertEqual(manage.validate_backup(root),root)
   (root/'database.dump').write_text('corrupted')
   with self.assertRaises(ValueError):manage.validate_backup(root)

 def test_archive_cannot_escape_or_create_link(self):
  for entry,kind in [('../escape',None),('/absolute',None),('link',tarfile.SYMTYPE),('hardlink',tarfile.LNKTYPE),('device',tarfile.CHRTYPE)]:
   with self.subTest(entry=entry),tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);self.fixture(root,entry,kind)
    with self.assertRaises(ValueError):manage.validate_backup(root)

 def test_backup_manifest_must_be_exact_and_files_must_not_be_symlinks(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.fixture(root)
   manifest=json.loads((root/'manifest.json').read_text())
   manifest['files']['../../escape']='a'*64
   (root/'manifest.json').write_text(json.dumps(manifest))
   with self.assertRaises(ValueError):manage.validate_backup(root)

 def test_operator_tool_cannot_target_hosted_or_shared_volumes(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);root.chmod(0o700)
   (root/'runtime.json').write_text(json.dumps({'Instance':{'Mode':'Hosted'}}))
   with self.assertRaises(ValueError):manage.installation(root,'talkrax-test')
   (root/'runtime.json').write_text(json.dumps({'Instance':{'Mode':'Independent'}}))
   (root/'compose.json').write_text(json.dumps({'services':{key:{} for key in manage.SERVICES},'volumes':{'storage':{'external':True}}}))
   with self.assertRaises(ValueError):manage.installation(root,'talkrax-test')

 def test_project_name_cannot_select_arbitrary_resources(self):
  with tempfile.TemporaryDirectory() as tmp:
   for project in ('','talkrax-live;echo bad','../talkrax','not-talkrax'):
    with self.subTest(project=project),self.assertRaises(ValueError):
     manage.installation(Path(tmp),project)

if __name__=='__main__':unittest.main()
