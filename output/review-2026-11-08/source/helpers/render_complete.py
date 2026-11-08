from pathlib import Path
from dataclasses import asdict,replace
from datetime import datetime,timezone
import difflib,hashlib,json,os,re,shutil,subprocess,sys,traceback
root=Path.cwd();proof=root/"dist/wfz-release";external=root.parent/"template";frozen=proof/"renderer-snapshot";review=proof/"render-review-complete";project=review/"project";snapshot=project;output=project/"output"
review.mkdir(exist_ok=False)
project.mkdir()
shutil.copytree(frozen/"infrastructure",snapshot/"infrastructure")
def files(base):
    return sorted(p for p in base.rglob("*") if p.is_file() and not any(part in {"__pycache__",".pytest_cache",".ruff_cache",".DS_Store"} for part in p.relative_to(base).parts) and p.suffix not in {".pyc",".pyo"})
def hashes(base):return {p.relative_to(base).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files(base)}
before=json.loads((proof/"render-review/render-receipt.json").read_text())["renderer_files"]
assert before==hashes(snapshot/"infrastructure"),"existing frozen renderer differs from capture"
asset_inputs={}
for name in ("package.json","package-lock.json"):
    asset_inputs[name]=hashlib.sha256((external/name).read_bytes()).hexdigest()
    shutil.copy2(external/name,project/name)
for name in ("mathjax","@mathjax/mathjax-newcm-font"):
    original=external/"node_modules"/name;target=project/"node_modules"/name
    if any(path.is_symlink() for path in original.rglob("*")):raise RuntimeError("asset dependency contains symlinks")
    asset_inputs[name]=hashes(original)
    shutil.copytree(original,target)
    assert hashes(original)==hashes(target)==asset_inputs[name]
current=proof/"artifacts/current-complete"
inputs=hashes(current)
for role in ("manuscript","figures","data","reports"):
    shutil.copytree(current/role,output/role)
kit=Path("/Users/friedman/Documents/Codex/2026-10-17/fix/work/duckrabbit-tex-unblock")
manifest=json.loads((kit/"kit-manifest.json").read_text())
kit_results={name:hashlib.sha256((kit/name).read_bytes()).hexdigest()==expected for name,expected in manifest["kit_files_sha256"].items()}
assert all(kit_results.values()),kit_results
for name in ("var","config","cache","fonts","tmp","mpl","xdg-config"):(review/"runtime"/name).mkdir(parents=True,exist_ok=True)
os.environ.update({"TEXMFHOME":str(kit/"texmf"),"TEXMFVAR":str(review/"runtime/var"),"TEXMFCONFIG":str(review/"runtime/config"),"TEXMFOUTPUT":str(output/"pdf"),"VARTEXFONTS":str(review/"runtime/fonts"),"TEXMFCACHE":str(review/"runtime/cache"),"XDG_CACHE_HOME":str(review/"runtime/cache"),"XDG_CONFIG_HOME":str(review/"runtime/xdg-config"),"MPLCONFIGDIR":str(review/"runtime/mpl"),"TMPDIR":str(review/"runtime/tmp"),"PYTHONDONTWRITEBYTECODE":"1","PATH":"/Users/friedman/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"})
tools={}
for name in ("xelatex","kpsewhich","bibtex","pandoc","pdftoppm","pdftotext"):
    path=shutil.which(name)
    if path is None:raise RuntimeError("missing render tool "+name)
    tools[name]={"path":path,"sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest()}
for name in ("xelatex","kpsewhich"):assert tools[name]["sha256"]==manifest["pinned_toolchain_sha256"][name]["sha256"]
sys.path.insert(0,str(snapshot))
import yaml
from infrastructure.rendering.config import RenderingConfig
from infrastructure.rendering.pdf_renderer import PDFRenderer
from infrastructure.rendering.web_renderer import WebRenderer
from infrastructure.rendering.slides_renderer import SlidesRenderer
manuscript=output/"manuscript";overlay=[]
p=manuscript/"preamble.md";old=p.read_text();new=old.replace("/usr/local/texlive/2026/texmf-dist/fonts/truetype/public/juliamono/",str(kit/"texmf/fonts/truetype/public/juliamono")+"/")
assert new!=old;p.write_text(new);overlay.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile="canonical/preamble.md",tofile="review/preamble.md"))
p=manuscript/"config.yaml";old=p.read_text();config_data=yaml.safe_load(old);binding=json.loads((proof/"matrix-logs/release-audit-final.stdout").read_text())["source_binding"]
config_data["paper"]["subtitle"]+=" — unreleased 0.6.0 digital review; source "+binding["source_sha256"][:16]
config_data["paper"]["date"]="2026-11-08"
new=yaml.safe_dump(config_data,sort_keys=False,allow_unicode=True);p.write_text(new);overlay.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile="canonical/config.yaml",tofile="review/config.yaml"))
(review/"review-overlay.patch").write_text("".join(overlay))
config=RenderingConfig(manuscript_dir=str(manuscript),figures_dir=str(output/"figures"),output_dir=str(output),pdf_dir=str(output/"pdf"),web_dir=str(output/"web"),slides_dir=str(output/"slides"),template_dir=str(snapshot/"infrastructure/rendering/templates"),latex_compiler="xelatex",pandoc_path=tools["pandoc"]["path"],security_profile="trusted-local",web_asset_mode="local")
sections=sorted(p for p in manuscript.glob("*.md") if re.match(r"^\d{2}_",p.name))
assert len(sections)==11
state={"date":datetime.now(timezone.utc).isoformat(),"source_binding":binding,"renderer_files":before,"kit_files":kit_results,"tools":tools,"python":sys.version,"python_executable":sys.executable,"inputs":inputs,"overlay_sha256":hashlib.sha256((review/"review-overlay.patch").read_bytes()).hexdigest(),"config":asdict(config),"sections":[p.name for p in sections],"external_web_dependencies":asset_inputs,"outcomes":[]}
def save():(review/"render-receipt.json").write_text(json.dumps(state,indent=2)+"\n")
def step(name,fn):
    try:
        result=fn();state["outcomes"].append({"name":name,"status":"passed","output":str(result)});print(name,"passed",result,flush=True)
    except Exception as exc:
        state["outcomes"].append({"name":name,"status":"failed","error":type(exc).__name__+": "+str(exc),"traceback":traceback.format_exc()});print(name,"failed",str(exc),flush=True)
    save()
os.chdir(project)
import copy
seqsplit=subprocess.run(["kpsewhich","seqsplit.sty"],stdin=subprocess.DEVNULL,capture_output=True,text=True,check=True,timeout=30).stdout.strip()
if not seqsplit:raise RuntimeError("PDF table wrapping requires seqsplit.sty")
pdf_source=output/"pdf-manuscript";shutil.copytree(manuscript,pdf_source)
wrap_audit=[];wrappers={}
def pandoc_text(text,source_format,target_format):
    result=subprocess.run([tools["pandoc"]["path"],"--from",source_format,"--to",target_format,"--wrap=none"],input=text,capture_output=True,text=True,check=True,timeout=60)
    return result.stdout
escapes={"\\":r"\textbackslash{}","{":r"\{","}":r"\}","_":r"\_","#":r"\#","&":r"\&","$":r"\$","%":r"\%","~":r"\textasciitilde{}","^":r"\textasciicircum{}"}
def wrap_nodes(value):
    if isinstance(value,dict):
        if value.get("t") in {"Str","Code"}:
            text=value["c"] if value["t"]=="Str" else value["c"][1]
            if len(text)>=13 and (any(char in text for char in "_./:=") or re.fullmatch(r"[0-9a-f]{32,}",text)):
                escaped="".join(escapes.get(char,char) for char in text)
                rendered=(r"\texttt{\breakseq{"+escaped+"}}") if value["t"]=="Code" else r"\breakseq{"+escaped+"}"
                if rendered in wrappers and wrappers[rendered]!=value:raise RuntimeError("ambiguous table overlay mapping")
                wrappers[rendered]=copy.deepcopy(value)
                return {"t":"RawInline","c":["latex",rendered]}
        return {key:wrap_nodes(item) for key,item in value.items()}
    if isinstance(value,list):return [wrap_nodes(item) for item in value]
    return value
def restore_nodes(value):
    if isinstance(value,dict):
        if value.get("t")=="RawInline" and value["c"][0]=="latex" and value["c"][1] in wrappers:return wrappers[value["c"][1]]
        return {key:restore_nodes(item) for key,item in value.items()}
    if isinstance(value,list):return [restore_nodes(item) for item in value]
    return value
for original_section in sections:
    path=pdf_source/original_section.name;original=path.read_text();lines=original.splitlines(True);result=[];index=0
    while index<len(lines):
        if not lines[index].lstrip().startswith("|"):
            result.append(lines[index]);index+=1;continue
        stop=index
        while stop<len(lines) and lines[stop].lstrip().startswith("|"):stop+=1
        fragment="".join(lines[index:stop]);parsed=json.loads(pandoc_text(fragment,"markdown","json"))
        if not any(block.get("t")=="Table" for block in parsed["blocks"]):
            result.append(fragment);index=stop;continue
        adapted=wrap_nodes(parsed)
        assert restore_nodes(adapted)==parsed,"table transformation changed non-formatting semantics"
        rendered=pandoc_text(json.dumps(adapted),"json","markdown+pipe_tables-simple_tables-multiline_tables-grid_tables")
        roundtrip=json.loads(pandoc_text(rendered,"markdown","json"))
        assert restore_nodes(roundtrip)==parsed,"table Markdown round trip changed semantic AST"
        wrap_audit.append({"file":path.name,"source_line":index+1,"semantic_ast_sha256":hashlib.sha256(json.dumps(parsed,sort_keys=True).encode()).hexdigest(),"roundtrip_semantics_preserved":True})
        result.append(rendered.rstrip()+"\n");index=stop
    updated="".join(result);path.write_text(updated)
    overlay.extend(difflib.unified_diff(original.splitlines(True),updated.splitlines(True),fromfile="canonical/"+path.name,tofile="pdf-review/"+path.name))
p=pdf_source/"preamble.md";original=p.read_text();position=original.rfind("\n```");assert position>=0
updated=original[:position]+"\n"+r"\usepackage{seqsplit}"+"\n"+r"\providecommand{\breakseq}[1]{\seqsplit{#1}}"+"\n"+original[position:];p.write_text(updated)
overlay.extend(difflib.unified_diff(original.splitlines(True),updated.splitlines(True),fromfile="canonical/preamble.md",tofile="pdf-review/preamble.md"))
(review/"review-overlay.patch").write_text("".join(overlay))
state["overlay_sha256"]=hashlib.sha256((review/"review-overlay.patch").read_bytes()).hexdigest()
state["pdf_source_overlay"]={"scope":"table-only format AST; identical restored semantic AST including URI targets and math; no generated TeX edits","tables":wrap_audit,"distinct_wrapped_literals":len(wrappers),"seqsplit_file":seqsplit,"seqsplit_sha256":hashlib.sha256(Path(seqsplit).read_bytes()).hexdigest()}
pdf_config=replace(config,manuscript_dir=str(pdf_source));pdf_sections=[pdf_source/p.name for p in sections]
save()

sys.path.insert(0,str(proof))
from build_slide_overlay import make_slide_overlay
slide_source=output/"slides-manuscript"
slide_audit=make_slide_overlay(manuscript,slide_source,Path(tools["pandoc"]["path"]))
(review/"slides-overlay-audit.json").write_text(json.dumps(slide_audit,indent=2)+"\n")
(review/"slides-overlay.patch").write_text("".join(slide_audit["patches"].values()))
state["slides_source_overlay"]={"helper_sha256":hashlib.sha256((proof/"build_slide_overlay.py").read_bytes()).hexdigest(),"audit_sha256":hashlib.sha256((review/"slides-overlay-audit.json").read_bytes()).hexdigest(),"counts":slide_audit["counts"],"assertions":slide_audit["assertions"]};save()

step("pdf",lambda:PDFRenderer(pdf_config).render_combined(pdf_sections,pdf_source,project_name="DuckRabbit-0.6.0-review"))
step("html",lambda:WebRenderer(config).render_combined(sections,manuscript,project_name="DuckRabbit-0.6.0-review"))
slide_config=replace(config,manuscript_dir=str(slide_source))
slides=SlidesRenderer(slide_config)
for original_section in sections:
    section=slide_source/original_section.name
    for kind in ("beamer","revealjs"):
        step("slides-"+section.stem+"-"+kind,lambda section=section,kind=kind:slides.render(section,output_format=kind,manuscript_dir=slide_source,figures_dir=output/"figures"))
assert before==hashes(snapshot/"infrastructure"),"renderer snapshot changed"
assert inputs==hashes(current),"canonical inputs changed"
assert all(hashlib.sha256((kit/name).read_bytes()).hexdigest()==expected for name,expected in manifest["kit_files_sha256"].items())
for name,module in list(sys.modules.items()):
    if name.startswith("infrastructure") and getattr(module,"__file__",None):assert Path(module.__file__).resolve().is_relative_to(snapshot),name
for name in ("mathjax","@mathjax/mathjax-newcm-font"):
    destination=output/"web/assets/mathjax-4.0.0"/("mathjax" if name=="mathjax" else "newcm")
    for pattern in ("LICENSE*","COPYING*","OFL*","COPYRIGHT*"):
        for path in (project/"node_modules"/name).glob(pattern):
            if path.is_file():shutil.copy2(path,destination/path.name)
for name in ("package.json","package-lock.json"):assert hashlib.sha256((project/name).read_bytes()).hexdigest()==asset_inputs[name]
for name in ("mathjax","@mathjax/mathjax-newcm-font"):assert hashes(project/"node_modules"/name)==asset_inputs[name]
state["outputs"]=hashes(output);state["frozen_renderer_unchanged"]=True;state["canonical_inputs_unchanged"]=True;save()
sys.exit(any(row["status"]!="passed" for row in state["outcomes"]))
