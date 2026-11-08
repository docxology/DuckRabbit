from pathlib import Path
from dataclasses import replace
import hashlib,json,os,re,shutil,sys,traceback
root=Path.cwd();proof=root/"dist/wfz-release";review=proof/"render-review-complete";project=review/"project";snapshot=project;output=project/"output";current=proof/"artifacts/current-complete"
state=json.loads((review/"render-receipt.json").read_text());before=state["renderer_files"];inputs=state["inputs"];tools=state["tools"];asset_inputs=state["external_web_dependencies"]
def files(base):return sorted(p for p in base.rglob("*") if p.is_file() and not any(part in {"__pycache__",".pytest_cache",".ruff_cache",".DS_Store"} for part in p.relative_to(base).parts) and p.suffix not in {".pyc",".pyo"})
def hashes(base):return {p.relative_to(base).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files(base)}
assert hashes(snapshot/"infrastructure")==before;assert hashes(current)==inputs
kit=Path("/Users/friedman/Documents/Codex/2026-10-17/fix/work/duckrabbit-tex-unblock");manifest=json.loads((kit/"kit-manifest.json").read_text())
os.environ.update({"TEXMFHOME":str(kit/"texmf"),"TEXMFVAR":str(review/"runtime/var"),"TEXMFCONFIG":str(review/"runtime/config"),"TEXMFOUTPUT":str(output/"pdf"),"VARTEXFONTS":str(review/"runtime/fonts"),"TEXMFCACHE":str(review/"runtime/cache"),"XDG_CACHE_HOME":str(review/"runtime/cache"),"XDG_CONFIG_HOME":str(review/"runtime/xdg-config"),"MPLCONFIGDIR":str(review/"runtime/mpl"),"TMPDIR":str(review/"runtime/tmp"),"PYTHONDONTWRITEBYTECODE":"1","PATH":"/Users/friedman/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"})
sys.path.insert(0,str(snapshot));sys.path.insert(0,str(proof))
from infrastructure.rendering.config import RenderingConfig
from infrastructure.rendering.pdf_renderer import PDFRenderer
from infrastructure.rendering.web_renderer import WebRenderer
from infrastructure.rendering.slides_renderer import SlidesRenderer
from build_slide_overlay import make_slide_overlay
config=RenderingConfig(**state["config"]);manuscript=output/"manuscript";sections=[manuscript/name for name in state["sections"]];pdf_source=output/"pdf-manuscript";pdf_config=replace(config,manuscript_dir=str(pdf_source));pdf_sections=[pdf_source/p.name for p in sections]
def save():(review/"render-receipt.json").write_text(json.dumps(state,indent=2)+"\n")
def step(name,fn):
 try:
  result=fn();state["outcomes"].append({"name":name,"status":"passed","output":str(result)});print(name,"passed",result,flush=True)
 except Exception as exc:
  state["outcomes"].append({"name":name,"status":"failed","error":type(exc).__name__+": "+str(exc),"traceback":traceback.format_exc()});print(name,"failed",str(exc),flush=True)
 save()
os.chdir(project)
import copy
import build_slide_overlay as adapter
source=output/"slides-manuscript";flat=output/"slides-flat-manuscript";shutil.copytree(source,flat)
marker="data-duckrabbit-slide-proof";format_audit=[]
def pandoc(text,from_,to_):
 import subprocess
 return subprocess.run([tools["pandoc"]["path"],"--from",from_,"--to",to_,"--wrap=preserve","--standalone"],input=text,text=True,capture_output=True,check=True,timeout=60).stdout
def leaves(doc):
 kinds={"Str","Space","SoftBreak","LineBreak","Code","CodeBlock","Math","RawInline","RawBlock","Cite","Link","Image"}
 return [node for node in adapter._nodes(doc) if node["t"] in kinds]
for section in source.glob("[0-9][0-9]_*.md"):
 document=json.loads(pandoc(section.read_text(),adapter._READER,"json"));original=copy.deepcopy(document);renames={}
 def lift(blocks):
  result=[]
  for block in blocks:
   if block["t"]=="Div":
    attr,children=block["c"]
    if attr[0].startswith("ref-") and section.name=="99_references.md":
     renamed="slide-source-"+attr[0][4:];renames[attr[0]]=renamed;attr[0]=renamed
    if any(key==marker for key,_ in attr[2]):
     kept=[attr[0],attr[1],[[key,value] for key,value in attr[2] if key!=marker]]
     if kept != ["",[],[]]:result.append({"t":"Div","c":[kept,[]]})
     result.extend(lift(children))
    else:
     block["c"][1]=lift(children);result.append(block)
   else:result.append(block)
  return result
 document["blocks"]=lift(document["blocks"])
 for node in adapter._nodes(document):
  if node["t"]=="Link" and node["c"][2][0].startswith("#"):
   target=node["c"][2][0][1:]
   if target in renames:node["c"][2][0]="#"+renames[target]
 restored=copy.deepcopy(document)
 for node in adapter._nodes(restored):
  if node["t"]=="Link":
   for old,new in renames.items():
    if node["c"][2][0]=="#"+new:node["c"][2][0]="#"+old
 adapter._require_equal(leaves(original),leaves(restored),section.name+" flat-render visible/literal content")
 text=pandoc(json.dumps(document),"json",adapter._WRITER);decoded=json.loads(pandoc(text,adapter._READER,"json"))
 adapter._require_equal(document,decoded,section.name+" flat-render complete source roundtrip")
 (flat/section.name).write_text(text)
 format_audit.append({"file":section.name,"source_sha256":hashlib.sha256(section.read_bytes()).hexdigest(),"render_source_sha256":hashlib.sha256(text.encode()).hexdigest(),"visible_and_literal_content_unchanged":True,"roundtrip_preserved":True,"reserved_anchor_renames":renames})
(review/"flat-slide-source-audit.json").write_text(json.dumps(format_audit,indent=2)+"\n")
changed={"03_results","07_publication_audit","09_appendix_catalog","99_references"};names={"slides-"+name+"-"+kind for name in changed for kind in ("beamer","revealjs")}
state.setdefault("superseded_outcomes",[]).extend(row for row in state["outcomes"] if row["name"] in names);state["outcomes"]=[row for row in state["outcomes"] if row["name"] not in names]
archive=review/"attempts/nested-frame-compile";archive.mkdir(exist_ok=False)
for name in changed:
 for path in (output/"slides").glob(name+"_slides.*"):shutil.move(path,archive/path.name)
slides=SlidesRenderer(replace(config,manuscript_dir=str(flat)))
for name in sorted(changed):
 section=flat/(name+".md")
 for kind in ("beamer","revealjs"):step("slides-"+name+"-"+kind,lambda section=section,kind=kind:slides.render(section,output_format=kind,manuscript_dir=flat,figures_dir=output/"figures"))
assert before==hashes(snapshot/"infrastructure");assert inputs==hashes(current)
state["flat_slide_source"]={"audit_sha256":hashlib.sha256((review/"flat-slide-source-audit.json").read_bytes()).hexdigest(),"used_decks":sorted(changed),"scope":"Lift proof-only Div wrappers to top-level frame boundaries; rename reserved ref- presentation anchors, never edit generated TeX."}
state["outputs"]=hashes(output);state["frozen_renderer_unchanged"]=True;state["canonical_inputs_unchanged"]=True;save()
raise SystemExit(any(row["status"]!="passed" for row in state["outcomes"]))
