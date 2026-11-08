from pathlib import Path
import json,os,subprocess,sys,time
root=Path.cwd();proof=root/'dist/wfz-release';logs=proof/'citation-final-logs';logs.mkdir(exist_ok=False);records=[]
def run(name,argv,cwd=root,timeout=300):
 argv=list(map(str,argv));start=time.monotonic()
 with (logs/(name+'.stdout')).open('w') as out,(logs/(name+'.stderr')).open('w') as err:
  p=subprocess.run(argv,cwd=cwd,stdin=subprocess.DEVNULL,stdout=out,stderr=err,timeout=timeout)
 records.append({'name':name,'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'seconds':time.monotonic()-start});(proof/'receipts/citation-final-results.json').write_text(json.dumps(records,indent=2)+'\n');print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError('failed '+name)
p=root/'.venv/bin/python';package=proof/'package-citation-final';current=proof/'artifacts/current-citation-final'
run('ruff',[p,'-B','-m','ruff','check','src','scripts','tests'])
run('lock-check',['uv','lock','--check','--offline'])
run('build',['uv','build','--offline','--no-build-isolation','--python',p,'--out-dir',package])
for version in ('3.11','3.12','3.14'):
 python=proof/('compat-'+version)/'bin/python'
 run('install-'+version,['uv','pip','install','--offline','--no-deps','--reinstall-package','duckrabbit','--python',python,package/'duckrabbit-0.6.0-py3-none-any.whl'])
 run('deps-'+version,['uv','pip','check','--python',python])
 run('suite-'+version,[python,'-B','-m','pytest','tests','--cov=duckrabbit','--cov-report=term-missing','--cov-report=json:'+str(proof/('coverage-citation-final-'+version+'.json'))])
run('suite-3.15',[p,'-B','-m','pytest','tests','--cov=duckrabbit','--cov-report=term-missing','--cov-report=json:'+str(proof/'coverage-citation-final-3.15.json')])
run('publication',[p,'-B','scripts/generate_publication_outputs.py','--output-dir',current])
run('manuscript',[p,'-B','scripts/generate_manuscript_variables.py','--output-dir',current])
run('scholarship-offline',[p,'-B','scripts/validate_scholarship.py'])
run('release-audit',[p,'-B','-m','duckrabbit','audit','--output-root',current,'--release'])
run('synthetic-cli',[p,'-B','-m','duckrabbit','synthetic-psychophysics','--output',current/'data/synthetic_psychophysics_cli.json'])
smoke=proof/'wheel-smoke-citation-final';smoke.mkdir(exist_ok=False);w=proof/'compat-3.11/bin/python'
run('wheel-api',[w,'-I','-B','-c',"import pathlib,sys,json,duckrabbit;from duckrabbit.evidence import load_evidence_matrix;from duckrabbit.canonical import canonical_digest;from duckrabbit.generators import DuckRabbitParams,generate_duck_rabbit;assert pathlib.Path(duckrabbit.__file__).resolve().is_relative_to(pathlib.Path(sys.prefix).resolve());assert duckrabbit.__version__=='0.6.0';a=generate_duck_rabbit(DuckRabbitParams());s,e=load_evidence_matrix();assert len(s)==36 and len(e)==18;print(json.dumps({'python':sys.version,'module':duckrabbit.__file__,'digest':canonical_digest(a),'sources':len(s),'entries':len(e)}))"],cwd=smoke)
run('wheel-list',[w,'-I','-B','-m','duckrabbit','list','--json'],cwd=smoke)
run('wheel-generate',[w,'-I','-B','-m','duckrabbit','generate','visual.duck_rabbit','--output-dir',smoke/'media','--format','npz'],cwd=smoke)
run('wheel-verify',[w,'-I','-B','-m','duckrabbit','verify',smoke/'media/visual_duck_rabbit.npz.json'],cwd=smoke)
media=proof/'artifacts/media-citation-final'
for folder,identifier,fmt,stem in [('image','visual.duck_rabbit','png','visual_duck_rabbit'),('audio','audio.missing_fundamental','wav','audio_missing_fundamental'),('temporal','visual.apparent_motion','gif','visual_apparent_motion'),('audiovisual','audiovisual.sound_induced_flash','mp4','audiovisual_sound_induced_flash'),('canonical','visual.duck_rabbit','npz','visual_duck_rabbit')]:
 run('generate-'+folder,[p,'-B','-m','duckrabbit','generate',identifier,'--output-dir',media/folder,'--format',fmt])
 path=media/folder/(stem+'.'+fmt)
 run('inspect-'+folder,[p,'-B','-m','duckrabbit','inspect',path]);run('verify-'+folder,[p,'-B','-m','duckrabbit','verify',str(path)+'.json'])
frames=media/'all-video-frames';frames.mkdir(exist_ok=False);video=media/'audiovisual/audiovisual_sound_induced_flash.mp4'
run('video-probe',['ffprobe','-v','error','-show_streams','-show_frames','-of','json',video])
run('decode-all-video-frames',['ffmpeg','-hide_banner','-loglevel','error','-i',video,'-map','0:v:0','-fps_mode','passthrough','-frames:v','8',frames/'frame-%02d.png'])
run('decode-actual-av-audio',['ffmpeg','-hide_banner','-loglevel','error','-i',video,'-map','0:a:0','-c:a','pcm_f32le',frames/'decoded-audio.wav'])
probe=json.loads((logs/'video-probe.stdout').read_text());video_frames=[f for f in probe['frames'] if f['media_type']=='video'];images=sorted(frames.glob('frame-*.png'))
if len(images)!=len(video_frames):raise RuntimeError('not every video frame decoded')
from PIL import Image,ImageDraw
import numpy as np,wave
sheet=Image.new('RGB',(len(images)*176,200),'white');draw=ImageDraw.Draw(sheet);frame_stats=[]
for index,(path,frame) in enumerate(zip(images,video_frames,strict=True)):
 image=Image.open(path).convert('RGB');values=np.asarray(image);image.thumbnail((168,168));sheet.paste(image,(index*176,0));timestamp=frame['best_effort_timestamp_time'];draw.text((index*176,175),f'{index}: {timestamp}s',fill='black');frame_stats.append({'frame':index,'seconds':timestamp,'mean_decoded_code_value':float(values.mean()),'size':list(values.shape)})
sheet.save(frames/'all-frame-contact.png')
with wave.open(str(media/'audio/audio_missing_fundamental.wav'),'rb') as wav:
 rate=wav.getframerate();channels=wav.getnchannels();width=wav.getsampwidth();n=wav.getnframes();raw=wav.readframes(n)
 samples=np.frombuffer(raw,dtype={2:'<i2',4:'<i4'}[width]).reshape(-1,channels).astype(np.float64);samples/=float(2**(8*width-1)-1);signal=samples.mean(axis=1);spectrum=np.abs(np.fft.rfft(signal));frequencies=np.fft.rfftfreq(n,1/rate);indices=np.argsort(spectrum)[-8:][::-1]
 audio={'rate':rate,'frames':n,'channels':channels,'pcm_width_bytes':width,'rms':float(np.sqrt(np.mean(samples*samples))),'peak':float(np.max(np.abs(samples))),'strongest_fft_hz':[float(frequencies[i]) for i in indices]}
(proof/'receipts/actual-media-citation-final.json').write_text(json.dumps({'video_frames':frame_stats,'stream_types':[s['codec_type'] for s in probe['streams']],'audio':audio,'limitations':'Decoded pixel/code-value and waveform/spectrum evidence only; not hearing, perception, playback calibration, or participant evidence.'},indent=2)+'\n')
print('ALL FINAL DELIVERY GATES PASSED',flush=True)

run('profile-final-citation',[p,'-B','scripts/profile_workloads.py','--workloads','canonical','video_metrics','observer','--iterations','1','--profile','--memory','--output-dir',proof/'performance-citation-final'])
from datetime import datetime,timezone
from duckrabbit.evidence import SourceRecord,_bibliography_entries
from duckrabbit.scholarship import compare_doi_metadata
import re
original=json.loads((proof/'receipts/adjunct-bibliography-identity.json').read_text());entries=_bibliography_entries(root/'docs/manuscript/references.bib');corrected=[]
for row in original['results']:
 row=dict(row);b=entries[row['key']];source=SourceRecord(key=row['key'],citation_key=row['key'],title=b['title'],source_type='theory',url=b['url'] or 'https://doi.org/'+b['doi'],doi=b['doi'],supports='Bibliographic identity observation only; not an evidence-graph assignment.',authors=tuple(re.split(r'\s+and\s+',b['author'])),year=int(b['year']))
 if row.get('metadata'):
  status=compare_doi_metadata(source,row['metadata']);row.update(verification_status=status.value,verified=status.value=='doi_metadata_match')
 row['expected']={'title':source.title,'authors':source.authors,'year':source.year};corrected.append(row)
report={'metadata_observed_at':original['observed_at'],'reevaluated_at':datetime.now(timezone.utc).isoformat(),'new_network_calls':0,'scope':'Re-evaluate retained primary DOI metadata against corrected complete bibliography and exact corporate-author comparator. Preserve unresolved/TLS failures; do not turn reachability into identity.','results':corrected}
(proof/'receipts/adjunct-bibliography-corrected.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'adjunct_count':len(corrected),'verified':sum(r['verified'] for r in corrected),'remaining':[{'key':r['key'],'status':r['verification_status']} for r in corrected if not r['verified']]}))
