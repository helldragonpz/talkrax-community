#!/usr/bin/env python3
"""Apply a reviewed independent-server image update with a mandatory recovery backup."""
import argparse
from contextlib import contextmanager
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.request
import manage

APPLICATION = ('api', 'worker', 'admin')
WRITERS = APPLICATION
DIGEST = re.compile(r'(?:[a-z0-9./:_-]+@)?sha256:[0-9a-f]{64}')
STATE = '.upgrade-state.json'


def read_json(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Expected a regular configuration file')
    return json.loads(path.read_text())


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.pending')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def lock(directory):
    fd = os.open(Path(directory) / '.operator.lock',
                 os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Another operator operation is active for this installation')
        yield
    finally:
        os.close(fd)


def output(args):
    return subprocess.check_output(args, text=True)


def owned_resources(directory, project):
    """Reject a project belonging to any other installation, including hosted."""
    ids = output(['docker', 'ps', '-aq', '--filter',
                  'label=com.docker.compose.project=' + project]).split()
    if not ids:
        raise ValueError('The selected project has no installed containers')
    records = json.loads(output(['docker', 'inspect'] + ids))
    expected = str(Path(directory).resolve() / 'compose.json')
    seen = set()
    for record in records:
        labels = record['Config'].get('Labels') or {}
        if labels.get('com.docker.compose.project.config_files') != expected:
            raise ValueError('Project containers belong to a different installation')
        service = labels.get('com.docker.compose.service')
        if service not in manage.SERVICES or labels.get('com.docker.compose.oneoff', '').lower() == 'true':
            raise ValueError('Unexpected project container')
        if service in seen:
            raise ValueError('Duplicate project service')
        seen.add(service)
        # No bind mount or external volume in the update input may select live data.
        for mount in record.get('Mounts', []):
            if mount['Type'] == 'volume' and not mount['Name'].startswith(project + '_'):
                # Redis declares an anonymous /data volume even when persistence is
                # disabled. Accept only that exact, exclusively mounted volume.
                anonymous_redis = (service == 'redis' and mount['Destination'] == '/data'
                                   and re.fullmatch(r'[a-f0-9]{64}', mount['Name']))
                users = output(['docker', 'ps', '-aq', '--no-trunc', '--filter',
                                'volume=' + mount['Name']]).split() if anonymous_redis else []
                if not anonymous_redis or users != [record['Id']]:
                    raise ValueError('Shared volume cannot be upgraded')
    if seen != manage.SERVICES:
        raise ValueError('All seven independent services must be installed')
    return records


def plan(directory, project, release_path, expected_sha256):
    directory, base = manage.installation(directory, project)
    if not re.fullmatch(r'[a-f0-9]{64}', expected_sha256 or ''):
        raise ValueError('Supply the release manifest SHA-256 from the reviewed release')
    path = Path(release_path)
    release = read_json(path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError('Release manifest checksum mismatch')
    if set(release) != {'format', 'releaseId', 'fromImages', 'images'} or release['format'] != 'talkrax-independent-update-v1':
        raise ValueError('Unsupported update manifest')
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}', release['releaseId']):
        raise ValueError('Invalid release identifier')
    for field in ('fromImages', 'images'):
        values = release[field]
        if not isinstance(values, dict) or set(values) != manage.SERVICES:
            raise ValueError('Incomplete update image inventory')
        if any(not isinstance(value, str) or not DIGEST.fullmatch(value) for value in values.values()):
            raise ValueError('Every release image must use an immutable digest')
    compose = read_json(directory / 'compose.json')
    current = {name: compose['services'][name]['image'] for name in manage.SERVICES}
    if current != release['fromImages']:
        raise ValueError('This release does not support the installed image inventory')
    for name in manage.SERVICES - set(APPLICATION):
        if release['images'][name] != current[name]:
            raise ValueError('Database, cache, proxy and media upgrades need a separate reviewed migration')
    changed = [name for name in APPLICATION if current[name] != release['images'][name]]
    if not changed:
        raise ValueError('The requested release is already installed')
    state = directory / STATE
    if state.exists() and read_json(state).get('status') != 'healthy':
        raise ValueError('An incomplete update requires recovery before another update')
    records = owned_resources(directory, project)
    if any(not record['State']['Running'] or record['State'].get('Paused') for record in records):
        raise ValueError('Update requires all independent services running and unpaused')
    # Verify the installed binaries match the claimed source release before mutation.
    for record in records:
        name = record['Config']['Labels']['com.docker.compose.service']
        image = json.loads(output(['docker', 'image', 'inspect', current[name]]))[0]
        if record['Image'] != image['Id']:
            raise ValueError('Running image does not match the installed configuration')
    return directory, base, compose, release, changed


def ensure_images(release):
    for name in APPLICATION:
        reference = release['images'][name]
        found = subprocess.run(['docker', 'image', 'inspect', reference],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if found.returncode:
            if reference.startswith('sha256:'):
                raise ValueError('Load the reviewed binary archive before applying this update')
            manage.execute(['docker', 'pull', reference], stdout=subprocess.DEVNULL)
        info = json.loads(output(['docker', 'image', 'inspect', reference]))[0]
        if reference.startswith('sha256:') and info['Id'] != reference:
            raise ValueError('Loaded image identity mismatch')
        if '@' in reference and reference not in info.get('RepoDigests', []):
            raise ValueError('Pulled image digest mismatch')


def wait_healthy(directory, base, release, timeout=120):
    runtime = read_json(directory / 'runtime.json')
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    deadline = time.monotonic() + timeout
    consecutive = 0
    while time.monotonic() < deadline:
        try:
            ids = output(base + ['ps', '-q'] + list(APPLICATION)).split()
            if len(ids) != len(APPLICATION):
                raise ValueError('Application services are not all running')
            records = json.loads(output(['docker', 'inspect'] + ids))
            api = None
            for record in records:
                name = record['Config']['Labels']['com.docker.compose.service']
                expected = json.loads(output(['docker', 'image', 'inspect', release['images'][name]]))[0]['Id']
                if not record['State']['Running'] or record['State'].get('Restarting') or record['Image'] != expected:
                    raise ValueError('Updated services not ready')
                if name == 'api':
                    api = record
            if api is None:
                raise ValueError('API missing')
            addresses = [v['IPAddress'] for k, v in api['NetworkSettings']['Networks'].items() if k.endswith('_edge')]
            if len(addresses) != 1:
                raise ValueError('Expected one independent edge network')
            origin = 'http://' + addresses[0] + ':8080'
            with opener.open(origin + '/api/health', timeout=3) as response:
                if json.load(response).get('status') != 'ok':
                    raise ValueError('API health check failed')
            with opener.open(origin + '/api/public/instance', timeout=3) as response:
                info = json.load(response)
                if info.get('mode') != 'Independent' or info.get('name') != runtime['Instance']['Name']:
                    raise ValueError('Independent instance identity changed')
            consecutive += 1
            if consecutive >= 3:
                return
        except (OSError, ValueError, KeyError, subprocess.CalledProcessError):
            consecutive = 0
        time.sleep(2)
    raise RuntimeError('Updated services failed health/identity checks')


def apply(directory, project, release_path, checksum, backup_path, timeout=120):
    directory = Path(directory).resolve()
    with lock(directory):
        directory, base, original, release, changed = plan(directory, project, release_path, checksum)
        backup_path = Path(backup_path).resolve()
        if backup_path.exists() or backup_path == directory or directory in backup_path.parents:
            raise ValueError('Backup must be a new directory outside the installation')
        ensure_images(release)
        state = {'status': 'preparing', 'releaseId': release['releaseId'],
                 'manifestSha256': checksum, 'backup': str(backup_path), 'startedAt': int(time.time())}
        atomic_json(directory / STATE, state)
        stopped = False
        candidate_started = False
        try:
            # Close ingress and stop writers before snapshot; leave data services running.
            stopped = True
            manage.execute(base + ['stop', 'caddy'] + list(WRITERS), stdout=subprocess.DEVNULL)
            manage.backup(directory, project, backup_path)
            manage.validate_backup(backup_path)
            state['status'] = 'backed-up'
            atomic_json(directory / STATE, state)
            candidate = copy.deepcopy(original)
            for name in APPLICATION:
                candidate['services'][name]['image'] = release['images'][name]
            atomic_json(directory / 'compose.json', candidate)
            manage.execute(base + ['config', '--quiet'])
            state['status'] = 'starting'
            atomic_json(directory / STATE, state)
            candidate_started = True
            manage.execute(base + ['up', '-d', '--no-deps'] + list(APPLICATION), stdout=subprocess.DEVNULL)
            wait_healthy(directory, base, release, timeout)
            manage.execute(base + ['up', '-d', '--no-deps', 'caddy'], stdout=subprocess.DEVNULL)
            # Ingress also has to stay running; an operator can verify public DNS/TLS separately.
            time.sleep(2)
            proxy_ids = output(base + ['ps', '-q', 'caddy']).split()
            if len(proxy_ids) != 1 or not json.loads(output(['docker', 'inspect'] + proxy_ids))[0]['State']['Running']:
                raise RuntimeError('Proxy failed to resume')
            state['status'] = 'healthy'
            state['completedAt'] = int(time.time())
            atomic_json(directory / STATE, state)
            return {'releaseId': release['releaseId'], 'updatedServices': changed,
                    'backup': str(backup_path), 'status': 'healthy'}
        except BaseException:
            if candidate_started:
                # A new binary may already have migrated the DB. Never start old code on it.
                subprocess.run(base + ['stop', 'caddy'] + list(WRITERS),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                state['status'] = 'recovery-required'
            else:
                # No new binary ran: the old data and original images are safe to resume.
                atomic_json(directory / 'compose.json', original)
                if stopped:
                    resumed = subprocess.run(base + ['up', '-d', '--no-deps'] + list(APPLICATION) + ['caddy'],
                                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    state['status'] = 'healthy' if resumed.returncode == 0 else 'recovery-required'
                else:
                    state['status'] = 'healthy'
            state['failedAt'] = int(time.time())
            atomic_json(directory / STATE, state)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--project', required=True)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--apply', action='store_true', help='Without this flag, print a read-only plan')
    parser.add_argument('--backup', type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    try:
        if args.apply:
            if args.backup is None:
                raise ValueError('--backup is required when applying an update')
            result = apply(args.directory, args.project, args.release, args.sha256, args.backup)
        else:
            _, _, _, release, changed = plan(args.directory, args.project, args.release, args.sha256)
            result = {'releaseId': release['releaseId'], 'changedServices': changed,
                      'apply': False, 'maintenanceWindowRequired': True}
        print(json.dumps(result, indent=2))
    except (ValueError, RuntimeError, subprocess.CalledProcessError, OSError) as error:
        # Subprocess arguments/configuration may contain secrets: do not echo them.
        print('Update failed. Inspect the private .upgrade-state.json and retain the recovery backup.')
        raise SystemExit(str(error) if isinstance(error, (ValueError, RuntimeError)) else 'Operator command failed')


if __name__ == '__main__':
    main()
