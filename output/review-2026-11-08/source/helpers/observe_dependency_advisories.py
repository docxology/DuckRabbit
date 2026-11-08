from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,tomllib,urllib.request
root=Path.cwd();proof=root/'dist/wfz-release';lock=root/'uv.lock';data=tomllib.loads(lock.read_text());rows=[]
def request(url,payload=None):
 body=json.dumps(payload).encode() if payload is not None else None
 req=urllib.request.Request(url,data=body,headers={'User-Agent':'DuckRabbit-release-audit/0.6.0','Content-Type':'application/json','Accept':'application/json'})
 with urllib.request.urlopen(req,timeout=6) as response:
  raw=response.read(2_000_001)
  if len(raw)>2_000_000:raise ValueError('response exceeds bounded metadata observation')
  return json.loads(raw)
for name,version in [(p['name'],p['version']) for p in data['package'] if p['name']!='duckrabbit']+[('setuptools','84.2.1')]:
 url=f'https://pypi.org/pypi/{name}/{version}/json';row={'name':name,'version':version,'ecosystem':'PyPI','url':url}
 try:
  result=request(url);assert result['info']['name'].lower().replace('_','-')==name and result['info']['version']==version
  row.update(status='observed',vulnerabilities=result['vulnerabilities'],last_serial=result['last_serial'])
 except Exception as error:row.update(status='unavailable',error=type(error).__name__+': '+str(error))
 rows.append(row)
for name,version in [('mathjax','4.0.0'),('@mathjax/mathjax-newcm-font','4.0.0'),('reveal.js','5.2.1')]:
 url='https://api.osv.dev/v1/query';row={'name':name,'version':version,'ecosystem':'npm','url':url}
 try:row.update(status='observed',vulnerabilities=request(url,{'package':{'name':name,'ecosystem':'npm'},'version':version}).get('vulns',[]))
 except Exception as error:row.update(status='unavailable',error=type(error).__name__+': '+str(error))
 rows.append(row)
record={'observed_at':datetime.now(timezone.utc).isoformat(),'uv_lock_sha256':hashlib.sha256(lock.read_bytes()).hexdigest(),'pyproject_sha256':hashlib.sha256((root/'pyproject.toml').read_bytes()).hexdigest(),'queries':rows,'limitations':'Dated primary metadata observation only. No guarantee of absence, exploitability certification, native-binary/OS/transitive-renderer security audit, or package-supply-chain authenticity.'}
(proof/'receipts/dependency-advisories.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'count':len(rows),'observed':sum(r['status']=='observed' for r in rows),'unavailable':[r for r in rows if r['status']!='observed'],'reported_vulnerabilities':[r for r in rows if r.get('vulnerabilities')]}))
raise SystemExit(0 if all(r['status']=='observed' and not r['vulnerabilities'] for r in rows) else 1)
