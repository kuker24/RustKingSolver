#!/usr/bin/env python3
"""
mitmproxy-advanced/scripts/agent.py
mitmproxy Addon Generator — generates inline modification addons.
MITRE ATT&CK: T1557 (Man-in-the-Middle), T1190 (Exploit Public-Facing App)
"""
import argparse, json, re, signal, sys, textwrap
try:
    from colorama import Fore, Style, init; init(autoreset=True)
except ImportError:
    class Fore: RED=GREEN=YELLOW=CYAN=MAGENTA=WHITE=RESET=""
    class Style: BRIGHT=DIM=NORMAL=RESET_ALL=""
    class init: autoreset=lambda: None
active = True
def signal_handler(sig, frame): global active; sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

ADDONS = {
"header_inject":{"desc":"Inject custom headers","p":{"request_headers":"{\"X-Test\":\"true\"}","response_headers":"{\"X-Powered-By\":\"mitmproxy\"}","target_hosts":"\"example.com\"","target_paths":"\"/\""},
"c":'''"""mitmproxy: HeaderInjector (T1557)"""
from mitmproxy import http
class HeaderInjector:
 def __init__(self):
  self.req_hdrs={request_headers}
  self.resp_hdrs={response_headers}
  self.hosts=[{target_hosts}]
  self.paths=[{target_paths}]
 def _match(self,f):
  h=f.request.pretty_host;p=f.request.path
  if self.hosts and h not in self.hosts and not any(h.endswith("."+x) for x in self.hosts): return False
  if self.paths and not any(p.startswith(x) for x in self.paths): return False
  return True
 def request(self,f):
  if self._match(f):
   for n,v in self.req_hdrs.items(): f.request.headers[n]=v
 def response(self,f):
  if self._match(f):
   for n,v in self.resp_hdrs.items(): f.response.headers[n]=v
addons=[HeaderInjector()]
'''},
"response_modifier":{"desc":"Modify response bodies","p":{"replacements":"{\"old\":\"new\"}","inject_script":"","inject_position":"body","content_types":"\"text/html\"","target_hosts":"\"example.com\""},
"c":'''"""mitmproxy: ResponseModifier (T1557)"""
from mitmproxy import http
import re
class ResponseModifier:
 def __init__(self):
  self.reps={replacements}
  self.script="{inject_script}"
  self.pos="{inject_position}"
  self.cts=[{content_types}]
  self.hosts=[{target_hosts}]
 def _match(self,f):
  if self.hosts and f.request.pretty_host not in self.hosts: return False
  ct=f.response.headers.get("content-type","")
  if self.cts and not any(t in ct for t in self.cts): return False
  return True
 def response(self,f):
  if not self._match(f): return
  t=f.response.get_text()
  if t is None: return
  for o,n in self.reps.items(): t=t.replace(o,n)
  if self.script:
   if self.pos=="head": t=t.replace("</head>",f"<script>{self.script}</script></head>")
   elif self.pos=="body": t=t.replace("</body>",f"<script>{self.script}</script></body>")
  f.response.set_text(t)
addons=[ResponseModifier()]
'''},
"request_filter":{"desc":"Filter/block requests","p":{"blocked_domains":"\"ads.x.com\"","blocked_extensions":"\".gif\",\".png\"","blocked_paths":"\"/analytics\"","redirect_rules":"{}","allowed_methods":"\"GET\",\"POST\""},
"c":'''"""mitmproxy: RequestFilter (T1190)"""
from mitmproxy import http
class RequestFilter:
 def __init__(self):
  self.block_domains=[{blocked_domains}]
  self.block_exts=[{blocked_extensions}]
  self.block_paths=[{blocked_paths}]
  self.redirects={redirect_rules}
  self.methods=[{allowed_methods}]
 def request(self,f):
  h=f.request.pretty_host;p=f.request.path;m=f.request.method
  if self.methods and m not in self.methods:
   f.response=http.Response.make(405,b"Not Allowed",{"Content-Type":"text/plain"}); return
  if self.block_domains and h in self.block_domains:
   f.response=http.Response.make(403,b"Blocked",{"Content-Type":"text/plain"}); return
  if self.block_exts:
   for e in self.block_exts:
    if p.endswith(e): f.response=http.Response.make(403,b"Blocked",{"Content-Type":"text/plain"}); return
  for pat,tgt in self.redirects.items():
   if pat in p: f.request.url=tgt; return
addons=[RequestFilter()]
'''},
"flow_logger":{"desc":"Log all flows","p":{"log_file":"","log_request_body":"False","log_response_body":"False","max_body_size":4096,"filter_hosts":""},
"c":'''"""mitmproxy: FlowLogger (T1557)"""
import json,datetime
from mitmproxy import http
class FlowLogger:
 def __init__(self):
  self.log_file="{log_file}"
  self.req_body={log_request_body}
  self.resp_body={log_response_body}
  self.max_sz={max_body_size}
  self.hosts=([{filter_hosts}]) if "{filter_hosts}" else []
 def _trunc(self,t):
  return t[:self.max_sz]+"..." if len(t)>self.max_sz else t
 def _write(self,e):
  print(f"[FL] {e.get('method','?')} {e.get('host','?')}{e.get('path','?')}")
  if self.log_file:
   with open(self.log_file,"a") as f: f.write(json.dumps(e)+"\\n")
 def request(self,f):
  if self.hosts and f.request.pretty_host not in self.hosts: return
  e={"ts":datetime.datetime.utcnow().isoformat(),"method":f.request.method,"host":f.request.pretty_host,"path":f.request.path,"headers":dict(f.request.headers)}
  if self.req_body: e["body"]=self._trunc(f.request.get_text() or "")
  self._write(e)
 def response(self,f):
  if self.hosts and f.request.pretty_host not in self.hosts: return
  e={"ts":datetime.datetime.utcnow().isoformat(),"status":f.response.status_code,"host":f.request.pretty_host,"path":f.request.path,"size":len(f.response.content)}
  if self.resp_body: e["body"]=self._trunc(f.response.get_text() or "")
  self._write(e)
addons=[FlowLogger()]
'''},
"flow_replay":{"desc":"Capture and replay flows","p":{"replay_mode":"capture","modify_headers":"{}","replay_count":1,"replay_delay":0.5},
"c":'''"""mitmproxy: FlowReplay (T1190)"""
import time
from mitmproxy import http
from mitmproxy import ctx
class FlowReplay:
 def __init__(self):
  self.captured=[]
  self.mode="{replay_mode}"
  self.mod_hdrs={modify_headers}
  self.count={replay_count}
  self.delay={replay_delay}
 def response(self,f):
  if self.mode!="capture": return
  self.captured.append(f)
  print(f"[FR] Captured {f.request.method} {f.request.pretty_host}{f.request.path}")
 def done(self):
  if self.mode!="replay": return
  print(f"[FR] Replaying {len(self.captured)} flows x{self.count}")
  for i in range(self.count):
   for f in self.captured:
    for n,v in self.mod_hdrs.items(): f.request.headers[n]=v
    ctx.master.commands.call("replay.client",[f])
    time.sleep(self.delay)
addons=[FlowReplay()]
'''},
}

def list_addons():
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n{Fore.WHITE}{Style.BRIGHT} mitmproxy Addon Templates{Style.RESET_ALL}\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    for aid,t in ADDONS.items():
        print(f"\n  {Fore.GREEN}{aid}{Style.RESET_ALL}\n    {t['desc']}")
        for pn,pv in t["p"].items(): print(f"      --param {pn}={pv}")
    print()

def generate(aid,params):
    t=ADDONS[aid];m={}
    for pn,pv in t["p"].items(): m[pn]=params.get(pn,pv)
    return textwrap.dedent(t["c"].format(**m)).lstrip()

def main():
    p=argparse.ArgumentParser(description="mitmproxy Addon Generator")
    p.add_argument("addon",nargs="?",default="list"); p.add_argument("--param","-p",action="append",default=[],dest="params"); p.add_argument("--output","-o"); p.add_argument("--dump",action="store_true")
    a=p.parse_args()
    if a.addon=="list": list_addons(); return
    if a.addon not in ADDONS: print(f"{Fore.RED}[!] Unknown{Style.RESET_ALL}"); list_addons(); sys.exit(1)
    params={}
    for pa in a.params:
        if "=" in pa: k,v=pa.split("=",1); params[k.strip()]=v.strip()
    code=generate(a.addon,params)
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n{Fore.WHITE}{Style.BRIGHT} {a.addon}.py{Style.RESET_ALL}\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n{code}")
    if a.output:
        with open(a.output,"w") as f: f.write(code+"\n")
        print(f"{Fore.GREEN}[+] {a.output}{Style.RESET_ALL}")
    if a.dump: print(json.dumps({"addon":a.addon,"code":code}))

if __name__ == "__main__":
    main()
