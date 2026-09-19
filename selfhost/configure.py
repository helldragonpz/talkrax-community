#!/usr/bin/env python3
"""Generate a new independent deployment. Never reuse or overwrite an installation."""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import secrets
from urllib.parse import urlsplit

def text(value, name, maximum=200):
    if not isinstance(value,str) or not value.strip() or len(value)>maximum or any(ord(c)<32 or ord(c)==127 for c in value):
        raise ValueError('Invalid '+name)
    return value.strip()

def https(value, name, origin=False):
    value=text(value,name,2048)
    uri=urlsplit(value)
    if uri.scheme!='https' or not uri.hostname or uri.username or uri.password or uri.fragment:
        raise ValueError(name+' must be an HTTPS address without credentials or fragments')
    try: port=uri.port
    except ValueError: raise ValueError('Invalid '+name+' port')
    if port is not None and not 1<=port<=65535: raise ValueError('Invalid '+name+' port')
    if origin and (uri.path not in ('','/') or uri.query or port not in (None,443)):
        raise ValueError(name+' must be an HTTPS origin on port 443')
    # Restrict Caddy site names to DNS names; do not interpolate arbitrary syntax.
    if origin and not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?',uri.hostname):
        raise ValueError('Invalid public hostname')
    return ('https://'+uri.hostname.lower()) if origin else value

def email(value,name):
    value=text(value,name)
    if not re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+',value): raise ValueError('Invalid '+name)
    return value

def generate(operator, images):
    required={'api','worker','admin','postgres','redis','livekit','caddy'}
    if set(images)!=required: raise ValueError('The release image inventory is incomplete')
    for key,value in images.items():
        if not isinstance(value,str) or not re.fullmatch(r'(?:[a-z0-9./:_-]+@)?sha256:[0-9a-f]{64}',value):
            raise ValueError('A reviewed immutable image digest is required for '+key)
    public=https(operator.get('publicUrl'),'publicUrl',True)
    media=https(operator.get('mediaUrl'),'mediaUrl',True)
    if public==media: raise ValueError('Use separate API and media DNS names')
    name=text(operator.get('name'),'name')
    owner=text(operator.get('operatorName'),'operatorName')
    contact=email(operator.get('contactEmail'),'contactEmail')
    privacy=https(operator.get('privacyUrl'),'privacyUrl')
    terms=https(operator.get('termsUrl'),'termsUrl')
    smtp=operator.get('smtp',{})
    smtp_host=text(smtp.get('host'),'smtp.host')
    if not re.fullmatch(r'[a-zA-Z0-9.-]+',smtp_host): raise ValueError('Invalid SMTP hostname')
    smtp_port=smtp.get('port',587)
    if isinstance(smtp_port,bool) or smtp_port not in (587,2525): raise ValueError('Use an SMTP STARTTLS submission port, 587 or 2525')
    smtp_user=text(smtp.get('username'),'smtp.username')
    smtp_password=text(smtp.get('password'),'smtp.password',4096)
    sender=email(smtp.get('fromAddress'),'smtp.fromAddress')
    ip=str(ipaddress.ip_address(text(operator.get('mediaPublicIp'),'mediaPublicIp')))
    if not ipaddress.ip_address(ip).is_global: raise ValueError('Media needs a verified public address')
    db_password=secrets.token_hex(32)
    redis_password=secrets.token_hex(32)
    api_key=secrets.token_hex(12)
    api_secret=secrets.token_hex(32)
    subnet=ipaddress.ip_network(operator.get('edgeSubnet','172.28.'+str(secrets.randbelow(256))+'.0/24'))
    if subnet.version!=4 or subnet.prefixlen!=24 or not subnet.subnet_of(ipaddress.ip_network('172.16.0.0/12')):
        raise ValueError('edgeSubnet must be a private /24 inside 172.16.0.0/12')
    proxy_ip=str(subnet.network_address+10)
    allowed=operator.get('adminAllowedCidrs')
    if not isinstance(allowed,list) or not 1<=len(allowed)<=20:
        raise ValueError('Supply adminAllowedCidrs for the operator VPN or administrator public IP')
    allowed=[ipaddress.ip_network(text(value,'adminAllowedCidrs'),strict=True) for value in allowed]
    if any(value.prefixlen==0 or value.is_multicast or value.is_unspecified for value in allowed):
        raise ValueError('Admin access must be restricted to explicit administrator networks')
    cfg={
      'ProductionMode':True,'SeedDevData':False,'PublicBaseUrl':public,'AppBaseUrl':public,
      'Instance':{'Mode':'Independent','Name':name,'OperatorName':owner,'ContactEmail':contact,'PrivacyUrl':privacy,'TermsUrl':terms},
      'ConnectionStrings':{'Postgres':'Host=postgres;Database=talkrax;Username=talkrax;Password='+db_password+';Maximum Pool Size=20'},
      'Redis':{'ConnectionString':'redis:6379,password='+redis_password+',abortConnect=false'},
      'Realtime':{'Provider':'redis'},
      'Security':{'TokenSigningKey':secrets.token_hex(32),'IpHashPepper':secrets.token_hex(32),
        'RequireEmailVerificationForLogin':True},
      'Storage':{'LocalPath':'/var/lib/talkrax/storage','SigningKey':secrets.token_hex(32)},
      'Admin':{'AllowDevBypass':False,'RequireMfa':True,'RequirePasskeyOrTotp':True,
        'BreakGlassEnabled':False,'AllowedCidrs':','.join(str(value) for value in allowed),
        'TrustedProxies':proxy_ip+'/32'},
      'Cors':{'AllowedOrigins':[public]},
      'ReverseProxy':{'KnownProxies':[proxy_ip]},
      'Email':{'Provider':'smtp','ExposeLocalOutbox':False,'Smtp':{
        'Host':smtp_host,'Port':smtp_port,'EnableSsl':True,'Username':smtp_user,
        'Password':smtp_password,'FromAddress':sender,'FromName':name}},
      'Billing':{'Provider':'paypal','PayPal':{'Enabled':False}},
      'Push':{'Firebase':{'Enabled':False}},
      'MediaHosting':{'AllowInsecureDevelopment':False,'Nodes':[{
        'Id':'independent-main','Label':name,'Region':'Operator configured',
        'PublicUrl':media.replace('https:','wss:',1),'ControlUrl':media,
        'ApiKey':api_key,'ApiSecret':api_secret,'Enabled':True,'DefaultForPlatform':True,
        'CommunityHosted':False,'SpaceIds':[],'MaxParticipantsPerRoom':8,
        'MaxActiveRooms':4,'MaxParticipantsPerNode':16,'MaxVideoPublishersPerRoom':2,
        'MaxVideoTracksPerParticipant':2,'MaxVideoBitrateKbps':1500,'EgressBudgetKbps':20000}]} }
    runtime=['./runtime.json:/run/talkrax/runtime.json:ro','storage:/var/lib/talkrax/storage']
    common={'restart':'unless-stopped','security_opt':['no-new-privileges:true'],
      'logging':{'driver':'json-file','options':{'max-size':'10m','max-file':'3'}}}
    def service(key,**options): return dict(common,image=images[key],**options)
    services={
      'postgres':service('postgres',environment={'POSTGRES_DB':'talkrax','POSTGRES_USER':'talkrax',
        'POSTGRES_PASSWORD_FILE':'/run/secrets/postgres-password'},
        volumes=['postgres:/var/lib/postgresql/data','./postgres-password:/run/secrets/postgres-password:ro'],
        healthcheck={'test':['CMD-SHELL','pg_isready -U talkrax -d talkrax'],'interval':'5s','timeout':'5s','retries':30},
        networks=['data']),
      'redis':service('redis',command=['redis-server','/run/redis.conf'],
        volumes=['./redis.conf:/run/redis.conf:ro'],networks=['data']),
      'api':service('api',environment={'ASPNETCORE_ENVIRONMENT':'Production','ASPNETCORE_URLS':'http://+:8080',
        'TALKRAX_MEDIA_CONFIG_FILE':'/run/talkrax/runtime.json'},volumes=runtime,
        depends_on={'postgres':{'condition':'service_healthy'},'redis':{'condition':'service_started'}},
        networks=['data','edge']),
      'worker':service('worker',environment={'DOTNET_ENVIRONMENT':'Production',
        'TALKRAX_MEDIA_CONFIG_FILE':'/run/talkrax/runtime.json'},volumes=runtime,
        depends_on={'postgres':{'condition':'service_healthy'}},networks=['data','edge']),
      'admin':service('admin',environment={'ASPNETCORE_ENVIRONMENT':'Production','ASPNETCORE_URLS':'http://+:8080',
        'TALKRAX_MEDIA_CONFIG_FILE':'/run/talkrax/runtime.json'},volumes=runtime,
        depends_on={'api':{'condition':'service_started'}},networks=['data','edge']),
      'livekit':service('livekit',command=['--config','/run/livekit.yaml'],
        volumes=['./livekit.yaml:/run/livekit.yaml:ro'],networks=['edge'],
        ports=['7881:7881/tcp','50000-50100:50000-50100/udp']),
      'caddy':service('caddy',volumes=['./Caddyfile:/etc/caddy/Caddyfile:ro','caddy-data:/data','caddy-config:/config'],
        ports=['80:80/tcp','443:443/tcp','443:443/udp'],
        networks={'edge':{'aliases':[urlsplit(media).hostname],'ipv4_address':proxy_ip}},
        depends_on={'api':{'condition':'service_started'},'livekit':{'condition':'service_started'}})
    }
    # This generator contains no official Talkrax host, credential, seed account
    # or source token. This package exposes no web client; native clients choose its origin.
    livekit={'port':7880,'rtc':{'tcp_port':7881,'port_range_start':50000,'port_range_end':50100,
       'node_ip':ip,'use_external_ip':False},'keys':{api_key:api_secret},'turn':{'enabled':False},
       'logging':{'level':'info'}}
    caddy=f"""{public} {{
    @admin path /admin /admin/*
    handle @admin {{
        reverse_proxy admin:8080 {{
            header_up -CF-Connecting-IP
            header_up -X-Real-IP
        }}
    }}
    handle /api/* {{
        reverse_proxy api:8080
    }}
    handle /gateway* {{
        reverse_proxy api:8080
    }}
    handle /health {{
        reverse_proxy api:8080
    }}
    handle {{
        respond "Independent Talkrax server. Connect using the Windows or Linux app." 200
    }}
}}
{media} {{
    reverse_proxy livekit:7880
}}
"""
    return {
      'runtime.json':json.dumps(cfg,indent=2)+'\n',
      'postgres-password':db_password+'\n',
      'redis.conf':'bind 0.0.0.0\nprotected-mode yes\nrequirepass '+redis_password+'\nappendonly no\nsave ""\n',
      # JSON is a YAML subset accepted by LiveKit's YAML configuration parser.
      'livekit.yaml':json.dumps(livekit,indent=2)+'\n',
      'Caddyfile':caddy,
      'compose.json':json.dumps({'name':'talkrax-independent','services':services,
        'networks':{'data':{'internal':True},'edge':{'ipam':{'config':[{'subnet':str(subnet)}]}}},
        'volumes':{k:{} for k in ['postgres','storage','caddy-data','caddy-config']}},indent=2)+'\n'}

def write_new(destination,files):
    destination=Path(destination)
    if os.name!='posix':
        raise ValueError('This installer currently requires Linux permissions; Windows ACL validation is pending')
    # Exclusive directory creation prevents overwriting installed keys or data.
    destination.mkdir(mode=0o700,parents=False,exist_ok=False)
    for name,content in files.items():
        fd=os.open(destination/name,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(fd,'w') as stream: stream.write(content)
        if name in {'runtime.json','postgres-password','redis.conf','livekit.yaml','Caddyfile'}:
            os.chmod(destination/name,0o444)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--operator',type=Path,required=True)
    parser.add_argument('--images',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try: files=generate(json.loads(args.operator.read_text()),json.loads(args.images.read_text()))
    except (ValueError,TypeError,KeyError) as error: raise SystemExit(str(error))
    write_new(args.output,files)
    print('Created a new private deployment directory. No services were started; no secrets were printed.')
if __name__=='__main__': main()
