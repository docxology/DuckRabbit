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
import subprocess,difflib
from infrastructure.rendering._slides_reveal_content import activate_hardened_reveal_mathjax,promote_display_math_labels,resolve_reveal_cross_references,reveal_reference_and_math_issues
from infrastructure.rendering._slides_crossref import parse_aux_label_numbers
from infrastructure.rendering._web_postprocess import normalize_figure_paths
from infrastructure.rendering._web_assets import MATHJAX_URL,MATHJAX_FONT_URL,MATHJAX_DYNAMIC_PREFIX
flat=output/"slides-flat-manuscript";header=review/"subscript-source-header.tex"
header.write_text("\\usepackage{newunicodechar}\n\\newunicodechar{ᵢ}{\\textsubscript{i}}\n\\newunicodechar{ₑ}{\\textsubscript{e}}\n")
css=output/"slides/digital-review.css";css.write_text(".reveal{font-size:28px}.reveal .slides section:not(.stack){height:100%;max-height:100%;overflow-y:auto;overflow-x:hidden;box-sizing:border-box;padding:0 20px 40px;text-align:left}.reveal .slides section.stack{overflow:visible}.reveal h1,.reveal h2{font-size:1.4em}.reveal img{max-width:100%;max-height:55vh;object-fit:contain}.reveal p,.reveal li,.reveal code,.reveal a{overflow-wrap:anywhere;word-break:break-word}.reveal pre{white-space:pre-wrap}\n")
base=SlidesRenderer(config)._process_runner;commands=[]
def runner(argv,*args,**kwargs):
 argv=list(argv)
 if "-t" in argv:
  kind=argv[argv.index("-t")+1]
  if kind=="beamer":argv.extend(["-H",str(header)])
  if kind=="revealjs":argv.extend(["--slide-level=2","-V","revealjs-url=https://unpkg.com/reveal.js@5.2.1","--mathjax="+MATHJAX_URL,"--css=digital-review.css"])
 commands.append(list(map(str,argv)))
 return base(argv,*args,**kwargs)
state.setdefault("superseded_outcomes",[]).extend(row for row in state["outcomes"] if row["name"].startswith("accessible-") or row["name"]=="slides-07_publication_audit-beamer" or row["name"].endswith("-revealjs"))
state["outcomes"]=[row for row in state["outcomes"] if not(row["name"].startswith("accessible-") or row["name"]=="slides-07_publication_audit-beamer" or row["name"].endswith("-revealjs"))]
archive=review/"attempts/before-runtime-overrides";archive.mkdir(exist_ok=False)
for path in (output/"slides").glob("*_slides.html"):shutil.move(path,archive/path.name)
for path in (output/"slides").glob("07_publication_audit_slides.*"):shutil.move(path,archive/path.name)
renderer=SlidesRenderer(replace(config,manuscript_dir=str(flat),slide_theme="white"),process_runner=runner)
step("slides-07_publication_audit-beamer",lambda:renderer.render(flat/"07_publication_audit.md",output_format="beamer",manuscript_dir=flat,figures_dir=output/"figures"))
labels=parse_aux_label_numbers(output/"pdf/_combined_manuscript.aux");assert labels
runtime=proof/"reveal-5.2.1/package";dest=output/"web/assets/reveal.js-5.2.1";shutil.copytree(runtime,dest)
html_records=[]
for section in sorted(flat.glob("[0-9][0-9]_*.md")):
 path=renderer.render(section,output_format="revealjs",manuscript_dir=flat,figures_dir=output/"figures")
 original=path.read_text();content=normalize_figure_paths(original)
 content=content.replace('data-src="../../output/figures/','data-src="../figures/')
 content=activate_hardened_reveal_mathjax(content);content=promote_display_math_labels(content);content=resolve_reveal_cross_references(content,labels,strict=True)
 issues=reveal_reference_and_math_issues(content)
 if issues:raise ValueError(str(issues))
 for old,new in {"https://unpkg.com/reveal.js@5.2.1":"../web/assets/reveal.js-5.2.1",MATHJAX_URL:"../web/assets/mathjax-4.0.0/mathjax/tex-chtml.js",MATHJAX_FONT_URL:"../web/assets/mathjax-4.0.0/newcm/chtml/woff2",MATHJAX_DYNAMIC_PREFIX:"../web/assets/mathjax-4.0.0/newcm/chtml/dynamic"}.items():content=content.replace(old,new)
 content=content.replace("window.MathJax = window.MathJax || {};","window.MathJax = window.MathJax || {};\nwindow.MathJax.loader = Object.assign({},window.MathJax.loader,{paths:{mathjax:'../web/assets/mathjax-4.0.0/mathjax'}});")
 path.write_text(content);(review/(section.stem+"-html-overlay.patch")).write_text("".join(difflib.unified_diff(original.splitlines(True),content.splitlines(True),fromfile="native/"+path.name,tofile="offline-review/"+path.name)))
 record={"name":"slides-"+section.stem+"-revealjs","status":"passed","output":str(path),"profile":"full-content digital archive, scrollable, not projection-certified","native_sha256":hashlib.sha256(original.encode()).hexdigest(),"sha256":hashlib.sha256(content.encode()).hexdigest(),"strict_canonical_reference_map":True};state["outcomes"].append(record);html_records.append(record);print(record["name"],"passed",flush=True)
state["runtime_overrides"]={"source_header_sha256":hashlib.sha256(header.read_bytes()).hexdigest(),"css_sha256":hashlib.sha256(css.read_bytes()).hexdigest(),"actual_commands":commands,"scope":"Existing public process_runner injection adds source -H, level2, white theme and pinned runtime; shared frozen HTML reference/math/path helpers; explicit local-asset relocation; no generated-TeX edits; no accessible-density claim."}
assert before==hashes(snapshot/"infrastructure");assert inputs==hashes(current)
state["outputs"]=hashes(output);save()
raise SystemExit(any(row["status"]!="passed" for row in state["outcomes"]))
