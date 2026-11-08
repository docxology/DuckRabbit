from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import urlsplit
import functools,hashlib,json,sys,threading
root=Path.cwd();proof=root/"dist/wfz-release";served=proof/"render-review-citation-final/project/output";finished=threading.Event();port=int(sys.argv[1]);marker=hashlib.sha256((served/"web/index.html").read_bytes()).hexdigest()
class Handler(SimpleHTTPRequestHandler):
 def do_GET(self):
  if self.path=="/__duckrabbit_proof_health":
   data=json.dumps({"source_html_sha256":marker}).encode();self.send_response(200);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(data)
  else:super().do_GET()
 def do_POST(self):
  if self.path!="/__duckrabbit_proof_finish" or self.headers.get("X-DuckRabbit-Proof")!=marker:self.send_error(403);return
  self.send_response(200);self.end_headers();self.wfile.write(b"finished");finished.set()
 def log_message(self,format,*args):print(json.dumps({"method":self.command,"path":urlsplit(self.path).path,"status":str(args[1]) if len(args)>1 else "event"}),flush=True)
server=ThreadingHTTPServer(("127.0.0.1",port),functools.partial(Handler,directory=str(served)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();print("DUCKRABBIT_PROOF_READY",flush=True)
ok=finished.wait(600);server.shutdown();server.server_close();thread.join();print("DUCKRABBIT_PROOF_FINISHED",ok,flush=True);raise SystemExit(0 if ok else 1)
