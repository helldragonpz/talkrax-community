import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('configure',Path(__file__).with_name('configure.py'))
configure=importlib.util.module_from_spec(spec)
spec.loader.exec_module(configure)

def fixture():
 return {'publicUrl':'https://guild.example','mediaUrl':'https://voice.guild.example',
  'name':'Guild','operatorName':'Independent Operator','contactEmail':'owner@guild.example',
  'privacyUrl':'https://policies.guild.example/privacy','termsUrl':'https://policies.guild.example/terms',
  'mediaPublicIp':'8.8.8.8','smtp':{'host':'smtp.guild.example','port':587,'username':'fixture',
  'password':'synthetic-not-a-real-credential','fromAddress':'mail@guild.example'},
  'adminAllowedCidrs':['192.0.2.24/32'],'edgeSubnet':'172.28.88.0/24'}

images={key:'registry.example/'+key+'@sha256:'+'a'*64
 for key in ['api','worker','admin','postgres','redis','livekit','caddy']}

class ConfigurationTests(unittest.TestCase):
 def test_independent_configuration_has_no_official_dependencies_or_public_database(self):
  files=configure.generate(fixture(),images)
  cfg=json.loads(files['runtime.json'])
  compose=json.loads(files['compose.json'])
  self.assertNotIn('talkrax.com',''.join(files.values()))
  self.assertEqual(cfg['Instance']['Mode'],'Independent')
  self.assertFalse(cfg['SeedDevData'])
  self.assertTrue(cfg['ProductionMode'])
  self.assertFalse(cfg['Billing']['PayPal']['Enabled'])
  self.assertFalse(cfg['Push']['Firebase']['Enabled'])
  self.assertEqual(cfg['ReverseProxy']['KnownProxies'],['172.28.88.10'])
  self.assertNotIn('web',compose['services'])
  self.assertIn('admin',compose['services'])
  self.assertEqual(cfg['Admin']['AllowedCidrs'],'192.0.2.24/32')
  self.assertEqual(cfg['Admin']['TrustedProxies'],'172.28.88.10/32')
  self.assertFalse(cfg['Admin']['BreakGlassEnabled'])
  self.assertIn('header_up -CF-Connecting-IP',files['Caddyfile'])
  self.assertIn('header_up -X-Real-IP',files['Caddyfile'])
  for service in ['postgres','redis','api','worker','admin']:
   self.assertNotIn('ports',compose['services'][service])
  self.assertTrue(compose['networks']['data']['internal'])
  self.assertEqual(compose['services']['caddy']['networks']['edge']['ipv4_address'],'172.28.88.10')
  secrets=[cfg['Security']['TokenSigningKey'],cfg['Security']['IpHashPepper'],
    cfg['Storage']['SigningKey'],cfg['MediaHosting']['Nodes'][0]['ApiSecret'],files['postgres-password'].strip()]
  self.assertEqual(len(set(secrets)),len(secrets))
  self.assertTrue(all(len(value)>=64 for value in secrets))
  other=json.loads(configure.generate(fixture(),images)['runtime.json'])
  self.assertNotEqual(cfg['Storage']['SigningKey'],other['Storage']['SigningKey'])

 def test_rejects_insecure_urls_syntax_injection_and_missing_operator_details(self):
  for field,value in [('publicUrl','http://guild.example'),('publicUrl','https://user:pass@guild.example'),
   ('publicUrl','https://guild.example/path'),('publicUrl','https://guild.example:444'),
   ('mediaUrl','https://guild.example'),('operatorName','Injected\nValue'),
   ('contactEmail','not-an-email'),('privacyUrl','javascript:alert(1)'),
   ('mediaPublicIp','127.0.0.1'),('edgeSubnet','0.0.0.0/0'),('adminAllowedCidrs',[]),('adminAllowedCidrs',['0.0.0.0/0'])]:
   data=fixture();data[field]=value
   with self.subTest(field=field,value=value), self.assertRaises(ValueError):
    configure.generate(data,images)
  for field in ['name','operatorName','contactEmail','privacyUrl','termsUrl']:
   data=fixture();del data[field]
   with self.subTest(missing=field),self.assertRaises(ValueError): configure.generate(data,images)

 def test_release_images_must_be_complete_and_immutable(self):
  data=copy.deepcopy(images);data['api']='registry.example/api:latest'
  with self.assertRaises(ValueError): configure.generate(fixture(),data)
  data=copy.deepcopy(images);del data['worker']
  with self.assertRaises(ValueError): configure.generate(fixture(),data)

 def test_new_install_cannot_overwrite_existing_keys(self):
  with tempfile.TemporaryDirectory() as root:
   path=Path(root)/'instance'
   files=configure.generate(fixture(),images)
   configure.write_new(path,files)
   before=(path/'runtime.json').read_bytes()
   with self.assertRaises(FileExistsError):
    configure.write_new(path,configure.generate(fixture(),images))
   self.assertEqual(before,(path/'runtime.json').read_bytes())
   self.assertEqual((path.stat().st_mode & 0o777),0o700)
   self.assertEqual(((path/'runtime.json').stat().st_mode & 0o777),0o444)

if __name__=='__main__': unittest.main()
