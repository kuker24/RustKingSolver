#!/usr/bin/env python3
"""
caido-scripting/scripts/agent.py
Caido Proxy Script Generator — generates JS/TS Caido workflow scripts.
MITRE ATT&CK: T1595 (Active Scanning)
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

RATE_FLAGS = {
"quiet": {"concurrency_scale": 0.1},
"moderate": {"concurrency_scale": 1.0},
"loud": {"concurrency_scale": 2.0},
}
def _rate_flags(profile="moderate"):
    return RATE_FLAGS.get(profile, RATE_FLAGS["moderate"])

WF = {
"repeater":{"desc":"Send through Repeater","t":"js","p":{"workflow_name":"CustomRepeater","description":"Custom repeater","request_template":"GET / HTTP/1.1\\nHost: x.com\\n\\n","expected_status":200,"additional_logic":"// custom logic"},
"c":"""import {{Repeater}} from "caido:workflow";
export function run(ctx){{
 const req=`{request_template}`;
 const r=new Repeater({{name:"{workflow_name}",request:req}});
 r.onResponse((resp)=>{{console.log(`[${{resp.getStatusCode()}}]`);{additional_logic}});
 r.send();
}}"""},
"intruder":{"desc":"Fuzzer with payloads","t":"ts","p":{"workflow_name":"Fuzzer","description":"Parameter fuzzer","request_template":"GET /search?q=FUZZ HTTP/1.1\\nHost: x.com\\n\\n","fuzz_position":"q","payload_list":"\"test\",\"admin\",\"' OR '1'='1\""},
"c":"""import {{Fuzzer}} from "caido:workflow";
const payloads=[{payload_list}];
export function run(){{
 const f=new Fuzzer({{name:"{workflow_name}",request:`{request_template}`}});
 for(const p of payloads) f.fuzz("{fuzz_position}",p);
 f.onResponse((r)=>console.log(`[${{r.getStatusCode()}}] ${{r.getBody().length}}b`));
 f.start();
}}"""},
"fuzzer":{"desc":"Advanced fuzzer with pattern matching","t":"ts","p":{"workflow_name":"SmartFuzzer","description":"Pattern fuzzer","request_template":"GET /api/x?p=FUZZ HTTP/1.1\\nHost: x.com\\n\\n","fuzz_position":"p","payload_list":"\"test\",\"1\",\"admin\",\"null\"","interesting_patterns":"\"error\",\"exception\"","concurrency":10,"expected_status":404},
"c":"""import {{Fuzzer}} from "caido:workflow";
const payloads=[{payload_list}],patterns=[{interesting_patterns}];
export function run(){{
 const f=new Fuzzer({{name:"{workflow_name}",request:`{request_template}`,concurrency:{concurrency}}});
 for(const p of payloads) f.fuzz("{fuzz_position}",p);
 f.onResponse((r)=>{{for(const pt of patterns) if(r.getBody().includes(pt)) console.warn(`[!] ${{pt}}`);if(r.getStatusCode()!=={expected_status}) console.log(`[!] ${{r.getStatusCode()}}`)}});
 f.start();
}}"""},
"request_modifier":{"desc":"Modify requests in-flight","t":"js","p":{"workflow_name":"Modifier","description":"Request modifier","modification_description":"Add headers","modification_code":"request.setHeader(\"X-Test\",\"true\");\nrequest.setPath(\"/api/test\");"},
"c":"""import {{Intercept}} from "caido:workflow";
export function run(ctx){{
 const req=ctx.request;
 {modification_code}
 console.log(`[+] Modified: ${{req.getPath()}}`);
 return req;
}}"""},
"response_analyzer":{"desc":"Analyze responses for security indicators","t":"js","p":{"workflow_name":"Analyzer","description":"Response security analyzer","indicators":"\"password\",\"secret\",\"token\",\"api_key\""},
"c":"""import {{Intercept}} from "caido:workflow";
const indicators=[{indicators}];
export function run(ctx){{
 const resp=ctx.response,body=resp.getBody(),headers=resp.getHeaders();
 for(const i of indicators) if(body.includes(i)) console.warn(`[!] ${{i}}`);
 for(const h of ["X-Content-Type-Options","X-Frame-Options","Content-Security-Policy"]) if(!headers[h.toLowerCase()]) console.warn(`[!] Missing ${{h}}`);
 return resp;
}}"""},
}

def list_wfs():
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n{Fore.WHITE}{Style.BRIGHT} Caido Workflow Templates{Style.RESET_ALL}\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    for wid,t in WF.items():
        print(f"\n  {Fore.GREEN}{wid}{Style.RESET_ALL} ({t['t']})\n    {t['desc']}")
        for pn,pv in t["p"].items(): print(f"      --param {pn}={pv}")
    print()

def infer(desc):
    d=desc.lower();h={"repeater":["repeater","send","manual"],"intruder":["intruder","fuzz","payload","multiple"],"fuzzer":["pattern","smart","advanced"],"request_modifier":["modify","header","rewrite","add"],"response_analyzer":["analyze","response","security header","inspect"]}
    best,best_s=None,0
    for wid,kws in h.items():
        s=sum(1 for kw in kws if kw in d)
        if s>best_s: best_s,best=s,wid
    return best,best_s

def generate(wid,params,profile="moderate"):
    t=WF[wid];m={}
    scale=_rate_flags(profile)["concurrency_scale"]
    for pn,pv in t["p"].items():
        if pn=="concurrency" and "concurrency" not in params:
            pv=max(1,int(pv*scale))
        m[pn]=params.get(pn,pv)
    return textwrap.dedent(t["c"].format(**m)).lstrip()

def main():
    p=argparse.ArgumentParser(description="Caido Workflow Generator")
    p.add_argument("workflow",nargs="?",default="list"); p.add_argument("--param","-p",action="append",default=[],dest="params"); p.add_argument("--infer","-i"); p.add_argument("--output","-o"); p.add_argument("--dump",action="store_true")
    noise=p.add_mutually_exclusive_group()
    noise.add_argument("--quiet",dest="profile",action="store_const",const="quiet",help="Low-noise: scales fuzzer concurrency down (default 10 -> 1)")
    noise.add_argument("--moderate",dest="profile",action="store_const",const="moderate",help="Moderate noise: fuzzer concurrency unchanged (default)")
    noise.add_argument("--loud",dest="profile",action="store_const",const="loud",help="High-noise: scales fuzzer concurrency up (default 10 -> 20)")
    p.set_defaults(profile="moderate")
    a=p.parse_args()
    if a.infer:
        wid,score=infer(a.infer)
        if wid is None: print(f"{Fore.RED}[!] No match{Style.RESET_ALL}"); list_wfs(); sys.exit(1)
        print(f"{Fore.GREEN}[+] Inferred: {wid} (score:{score}){Style.RESET_ALL}"); a.workflow=wid
    if a.workflow=="list": list_wfs(); return
    if a.workflow not in WF: print(f"{Fore.RED}[!] Unknown{Style.RESET_ALL}"); list_wfs(); sys.exit(1)
    params={}
    for pa in a.params:
        if "=" in pa: k,v=pa.split("=",1); params[k.strip()]=v.strip()
    code=generate(a.workflow,params,profile=a.profile)
    ext=WF[a.workflow]["t"]
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n{Fore.WHITE}{Style.BRIGHT} {a.workflow}.{ext}{Style.RESET_ALL}\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n{code}")
    if a.output:
        with open(a.output,"w") as f: f.write(code+"\n")
        print(f"{Fore.GREEN}[+] {a.output}{Style.RESET_ALL}")
    if a.dump: print(json.dumps({"workflow":a.workflow,"type":ext,"code":code}))

if __name__ == "__main__":
    main()
