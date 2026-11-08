from pathlib import Path
from collections import Counter
import hashlib,json,re,subprocess,sys
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser
from pypdf import PdfReader
from PIL import Image,ImageDraw
root=Path.cwd();review=root/"dist/wfz-release/render-review-citation-final";output=review/"project/output";qa=review/"qa";qa.mkdir(exist_ok=False)
old_qa=review/"qa";previous={};html_ids={}
class IDs(HTMLParser):
 def __init__(self):super().__init__();self.ids=set()
 def handle_starttag(self,tag,attrs):
  values=dict(attrs)
  if "id" in values:self.ids.add(values["id"])
def uri_allowed(parsed,pdf):
 if parsed.scheme in {"http","https"}:return bool(parsed.hostname) and parsed.username is None and parsed.password is None
 if parsed.scheme=="mailto":return bool(parsed.path)
 if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/") or parsed.query:return False
 target=(pdf.parent/unquote(parsed.path)).resolve()
 if not target.is_relative_to(output.resolve()) or not target.is_file():return False
 if parsed.fragment:
  if target.suffix.lower() not in {".html",".htm"}:return False
  if target not in html_ids:
   parser=IDs();parser.feed(target.read_text());html_ids[target]=parser.ids
  if unquote(parsed.fragment) not in html_ids[target]:return False
 return True
results=[]
for pdf in [output/"pdf/DuckRabbit-0.6.0-review_combined.pdf",*sorted((output/"slides").glob("*.pdf"))]:
    reader=PdfReader(pdf,strict=True);named=reader.named_destinations;page_refs={getattr(p.indirect_reference,"idnum",None) for p in reader.pages};broken=[];uris=[];internal=0;blank=[];missing_tokens=[];texts=[]
    def destination_ok(value):
        if isinstance(value,str):return value in named or value.lstrip("/") in named
        if isinstance(value,(list,tuple)) and value:
            first=value[0]
            return 0<=first<len(reader.pages) if isinstance(first,int) else getattr(first,"idnum",None) in page_refs
        return False
    for number,page in enumerate(reader.pages,1):
        text=page.extract_text() or "";texts.append(text)
        if not text.strip():blank.append(number)
        if re.search(r"\{\{[A-Z][A-Z0-9_]*\}\}",text) or "\ufffd" in text:missing_tokens.append(number)
        for item in page.get("/Annots",[]):
            annotation=item.get_object();action=annotation.get("/A")
            if action is not None:action=action.get_object()
            target=annotation.get("/Dest")
            if action and action.get("/S")=="/URI":
                parsed=urlsplit(str(action.get("/URI","")));uris.append({"scheme":parsed.scheme,"host":parsed.netloc,"path":parsed.path,"fragment":parsed.fragment,"allowed":uri_allowed(parsed,pdf)})
            elif action and action.get("/S")=="/GoTo":target=action.get("/D")
            elif action:broken.append({"page":number,"unsupported_action":str(action.get("/S"))})
            if target is not None:
                internal+=1
                if not destination_ok(target):broken.append({"page":number,"destination":str(target)})
    is_main=pdf.parent.name=="pdf";expected=set(re.findall(r"@[A-Za-z]+\{([^,]+),",(output/"manuscript/references.bib").read_text())) if is_main else set()
    missing=sorted(key for key in expected if "cite."+key not in named and "ref-"+key not in named)
    old=previous.get(pdf.relative_to(output).as_posix());unchanged=old is not None and old["sha256"]==hashlib.sha256(pdf.read_bytes()).hexdigest()
    directory=(old_qa if unchanged else qa)/("main" if is_main else pdf.stem)
    if unchanged:
        assert all(hashlib.sha256((old_qa/path).read_bytes()).hexdigest()==digest for path,digest in old["page_images"].items())
    else:directory.mkdir(exist_ok=False)
    command=["pdftoppm","-r","110" if is_main else "160","-png",str(pdf),str(directory/"page")]
    if not unchanged:subprocess.run(command,stdin=subprocess.DEVNULL,check=True,timeout=180,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    images=sorted(directory.glob("page-*.png"),key=lambda p:int(p.stem.split("-")[-1]));assert len(images)==len(reader.pages)
    sheets=[]
    for start in range(0,len(images),12):
        sheet=Image.new("RGB",(1000,4*350),(255,255,255));draw=ImageDraw.Draw(sheet)
        for index,path in enumerate(images[start:start+12]):
            with Image.open(path) as image:
                image=image.convert("RGB");image.thumbnail((318,320));x=(index%3)*333;y=(index//3)*350;sheet.paste(image,(x,y+22));draw.text((x+4,y+3),f"page {int(path.stem.split('-')[-1])}",fill=(0,0,0))
        target=directory/f"contact-{start//12+1:02}.png";sheet.save(target);sheets.append(target.relative_to(old_qa if unchanged else qa).as_posix())
    (directory/"extracted-text.txt").write_text("\n\f\n".join(texts))
    row={"raster_root":"../qa" if unchanged else ".","reused_byte_identical_pdf":unchanged,"path":pdf.relative_to(output).as_posix(),"sha256":hashlib.sha256(pdf.read_bytes()).hexdigest(),"pages":len(reader.pages),"named_destinations":len(named),"internal_links":internal,"external_uri_count":len(uris),"uri_schemes":dict(Counter(u["scheme"] for u in uris)),"unsupported_uri_schemes":[u for u in uris if not u["allowed"]],"broken_destinations":broken,"blank_text_pages":blank,"unresolved_token_pages":missing_tokens,"missing_bibliography_destinations":missing,"page_images":{p.relative_to(old_qa if unchanged else qa).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in images},"contact_sheets":sheets}
    results.append(row);(qa/"machine-review.json").write_text(json.dumps(results,indent=2)+"\n");print(json.dumps({key:row[key] for key in ("path","pages","internal_links","external_uri_count","broken_destinations","blank_text_pages","missing_bibliography_destinations")}),flush=True)
assert all(not r["broken_destinations"] and not r["unresolved_token_pages"] and not r["unsupported_uri_schemes"] and not r["missing_bibliography_destinations"] for r in results)
print("PDF_MACHINE_QA_PASSED",flush=True)
previous={r['path']:r for r in json.loads((root/'dist/wfz-release/render-review-delivery/qa/machine-review.json').read_text())};comparisons=[]
for row in results:
 old=previous[row['path']];same=[p for p,h in row['page_images'].items() if old['page_images'].get(p)==h];changed=[p for p,h in row['page_images'].items() if old['page_images'].get(p)!=h]
 comparisons.append({'path':row['path'],'previous_pdf_sha256':old['sha256'],'current_pdf_sha256':row['sha256'],'previous_pages':old['pages'],'current_pages':row['pages'],'same_rasters':same,'changed_rasters':changed,'scope':'Only byte-identical page rasters reuse prior visual coverage; all changed rasters require final review.'})
(qa/'source-correction-comparison.json').write_text(json.dumps(comparisons,indent=2)+'\n');print(json.dumps({'main':results[0]['pages'],'slides':sum(r['pages'] for r in results[1:]),'changed':[{'path':r['path'],'pages':r['changed_rasters']} for r in comparisons if r['changed_rasters']]}),flush=True)
