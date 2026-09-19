#!/usr/bin/env python3
"""Operate only an explicitly selected independent Talkrax installation (Linux)."""
import argparse, hashlib, ipaddress, json, os, secrets
from pathlib import Path
import re, shutil, subprocess, tarfile, time

CONFIG_FILES=('runtime.json','postgres-password','redis.conf','livekit.yaml','Caddyfile','compose.json')
BACKUP_FILES=CONFIG_FILES+('database.dump','storage.tar')
SERVICES={'api','worker','admin','postgres','redis','livekit','caddy'}

def execute(args,**kwargs):
 return subprocess.run(args,check=True,**kwargs)

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def installation(directory,project):
 directory=Path(directory).resolve()
 if os.name!='posix':raise ValueError('Linux is required; Windows ACL support is not released')
 if not re.fullmatch(r'talkrax-[a-z0-9][a-z0-9-]{2,55}',project):
  raise ValueError('Use a unique project name starting talkrax- and lowercase letters, numbers or hyphens')
 if (directory.stat().st_mode & 0o077)!=0:raise ValueError('Installation directory must have mode 0700')
 config=json.loads((directory/'runtime.json').read_text())
 if config.get('Instance',{}).get('Mode')!='Independent':
  raise ValueError('This tool cannot operate the hosted Talkrax deployment')
 compose=json.loads((directory/'compose.json').read_text())
 if set(compose.get('services',{}))!=SERVICES:raise ValueError('Unexpected service inventory')
 for service in compose['services'].values():
  if 'container_name' in service:raise ValueError('Explicit shared container names are not supported')
 for volume in compose.get('volumes',{}).values():
  if volume.get('external') or volume.get('name'):raise ValueError('Shared external volumes are not supported')
 return directory,['docker','compose','-p',project,'-f',str(directory/'compose.json')]

def backup(directory,project,destination):
 directory,base=installation(directory,project)
 destination=Path(destination).resolve()
 destination.mkdir(mode=0o700,exist_ok=False)
 running=subprocess.check_output(base+['ps','--services','--status','running'],text=True).split()
 writers=[s for s in ('api','worker','admin') if s in running]
 if 'postgres' not in running:raise ValueError('The selected independent database must be running')
 paused=False
 try:
  if writers:
   execute(base+['pause']+writers,stdout=subprocess.DEVNULL);paused=True
  for name in CONFIG_FILES:
   shutil.copyfile(directory/name,destination/name);(destination/name).chmod(0o600)
  with (destination/'database.dump').open('xb') as stream:
   execute(base+['exec','-T','postgres','pg_dump','-U','talkrax','-d','talkrax','-Fc','--no-owner','--no-acl'],stdout=stream)
  # The stopped helper mounts only this installation's storage, without networking.
  config=json.loads((directory/'compose.json').read_text())
  with (destination/'storage.tar').open('xb') as stream:
   execute(['docker','run','--rm','--network','none','--user','0','--entrypoint','tar',
    '--mount','type=volume,src='+project+'_storage,dst=/backup,readonly',
    config['services']['api']['image'],'-C','/backup','-cf','-','.'],stdout=stream)
  manifest={'format':'talkrax-independent-backup-v1','createdAt':int(time.time()),
    'files':{name:digest(destination/name) for name in BACKUP_FILES}}
  for name in BACKUP_FILES:(destination/name).chmod(0o600)
  (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  (destination/'manifest.json').chmod(0o600)
 finally:
  if paused:execute(base+['unpause']+writers,stdout=subprocess.DEVNULL)
 return destination

def validate_backup(source):
 source=Path(source).resolve()
 manifest=json.loads((source/'manifest.json').read_text())
 if manifest.get('format')!='talkrax-independent-backup-v1' or set(manifest.get('files',{}))!=set(BACKUP_FILES):
  raise ValueError('Unsupported or incomplete backup')
 for name in BACKUP_FILES:
  path=source/name
  if path.is_symlink() or not path.is_file() or digest(path)!=manifest['files'][name]:
   raise ValueError('Backup integrity check failed for '+name)
 # Never let a storage archive create links/devices or escape the restored volume.
 with tarfile.open(source/'storage.tar','r:') as archive:
  for entry in archive:
   parts=Path(entry.name).parts
   if Path(entry.name).is_absolute() or '..' in parts or not (entry.isfile() or entry.isdir()):
    raise ValueError('Unsafe storage archive entry')
 return source

def restore(source,directory,project):
 source=validate_backup(source)
 # Refuse any pre-existing resources for the selected project, including volumes.
 for kind in ('container','volume','network'):
  existing=subprocess.check_output(['docker',kind,'ls','-q','--filter','label=com.docker.compose.project='+project],text=True).strip()
  if existing:raise ValueError('Restore requires a new project with no existing containers, networks or volumes')
 directory=Path(directory).resolve();directory.mkdir(mode=0o700,exist_ok=False)
 for name in CONFIG_FILES:
  shutil.copyfile(source/name,directory/name)
  (directory/name).chmod(0o600 if name=='compose.json' else 0o444)
 # Keep signing/encryption credentials, but allocate a fresh bridge subnet.
 # The operator must separately decide public DNS/port cutover; default restore
 # starts data services only and cannot take over the active instance's ports.
 directory,base=installation(directory,project)
 config=json.loads((directory/'compose.json').read_text())
 network_ids=subprocess.check_output(['docker','network','ls','-q'],text=True).split()
 existing=json.loads(subprocess.check_output(['docker','network','inspect']+network_ids,text=True)) if network_ids else []
 occupied=[ipaddress.ip_network(item['Subnet']) for net in existing
  for item in (net.get('IPAM',{}).get('Config') or []) if item.get('Subnet')]
 for attempt in range(256):
  candidate=ipaddress.ip_network('10.203.'+str(secrets.randbelow(256))+'.0/24')
  if all(not candidate.overlaps(item) for item in occupied if item.version==4):break
 else:raise ValueError('No unused restore bridge subnet available')
 proxy=str(candidate.network_address+10)
 config['networks']['edge']['ipam']['config']=[{'subnet':str(candidate)}]
 config['services']['caddy']['networks']['edge']['ipv4_address']=proxy
 (directory/'compose.json').write_text(json.dumps(config,indent=2)+'\n')
 runtime_path=directory/'runtime.json'
 runtime=json.loads(runtime_path.read_text())
 runtime['ReverseProxy']['KnownProxies']=[proxy]
 runtime['Admin']['TrustedProxies']=proxy+'/32'
 runtime_path.chmod(0o600);runtime_path.write_text(json.dumps(runtime,indent=2)+'\n');runtime_path.chmod(0o444)
 execute(base+['up','-d','postgres'],stdout=subprocess.DEVNULL)
 for attempt in range(90):
  ready=subprocess.run(base+['exec','-T','postgres','pg_isready','-U','talkrax','-d','talkrax'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  if ready.returncode==0:break
  if attempt==89:raise RuntimeError('Restored database did not become ready')
  time.sleep(1)
 with (source/'database.dump').open('rb') as stream:
  execute(base+['exec','-T','postgres','pg_restore','-U','talkrax','-d','talkrax','--no-owner','--no-acl','--exit-on-error'],stdin=stream)
 # Compose has not created the storage volume yet.
 execute(['docker','volume','create','--label','com.docker.compose.project='+project,
  '--label','com.docker.compose.volume=storage',project+'_storage'],stdout=subprocess.DEVNULL)
 with (source/'storage.tar').open('rb') as stream:
  execute(['docker','run','--rm','-i','--network','none','--user','0','--entrypoint','tar',
    '--mount','type=volume,src='+project+'_storage,dst=/restore',
    config['services']['api']['image'],'-C','/restore','-xf','-'],stdin=stream)
 return directory

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--directory',type=Path,required=True)
 parser.add_argument('--project',required=True)
 sub=parser.add_subparsers(dest='operation',required=True)
 sub.add_parser('start');sub.add_parser('status')
 owner=sub.add_parser('appoint-owner');owner.add_argument('--email',required=True);owner.add_argument('--reason',required=True)
 save=sub.add_parser('backup');save.add_argument('--output',type=Path,required=True)
 recover=sub.add_parser('restore');recover.add_argument('--backup',type=Path,required=True)
 args=parser.parse_args()
 os.umask(0o077)
 if args.operation=='restore':
  restore(args.backup,args.directory,args.project)
  print('Backup restored to a new isolated project. Only its database is running. Review ports and DNS before start.')
  return
 directory,base=installation(args.directory,args.project)
 if args.operation=='start':execute(base+['up','-d'])
 elif args.operation=='status':execute(base+['ps'])
 elif args.operation=='appoint-owner':
  execute(base+['exec','-T','api','dotnet','Talkrax.Api.dll','bootstrap-owner',args.email,args.reason])
 elif args.operation=='backup':
  backup(directory,args.project,args.output)
  print('Backup verified and saved in a private directory. Protect it: it contains account data and instance keys.')

if __name__=='__main__':
 try:main()
 except (ValueError,FileExistsError) as error:raise SystemExit(str(error))
