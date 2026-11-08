from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,sys
root=Path.cwd();sys.path[:0]=[str(root/'src'),str(root/'.venv/lib/python3.15/site-packages')]
from duckrabbit.evidence import SourceRecord,_bibliography_entries,load_evidence_matrix
from duckrabbit.scholarship import audit_source
sources,_=load_evidence_matrix();known={s.citation_key for s in sources.values()};entries=_bibliography_entries(root/'docs/manuscript/references.bib');results=[]
for key,row in entries.items():
 if key in known:continue
 source=SourceRecord(key=key,citation_key=key,title=row['title'],source_type='theory',url=row['url'] or 'https://doi.org/'+row['doi'],doi=row['doi'],supports='Bibliographic identity observation only; no evidence-graph claim is assigned.',authors=tuple(re.split(r'\s+and\s+',row['author'])),year=int(row['year']))
 observed=audit_source(source,timeout=5);observed['expected']={'title':source.title,'authors':source.authors,'year':source.year};results.append(observed)
report={'observed_at':datetime.now(timezone.utc).isoformat(),'bibliography_sha256':hashlib.sha256((root/'docs/manuscript/references.bib').read_bytes()).hexdigest(),'scope':'All bibliography entries outside the36 evidence-source records, using the existing exact DOI/title/ordered-author/year comparator; no authority or gate override.','results':results}
(root/'dist/wfz-release/receipts/adjunct-bibliography-identity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'count':len(results),'verified':sum(r['verified'] for r in results),'statuses':[{'key':r['key'],'status':r['verification_status']} for r in results]}));raise SystemExit(0 if all(r['verified'] for r in results) else 1)
