#!/usr/bin/env python3
"""
ffuf-advanced/scripts/agent.py
ffuf Automation Tool — command builder, wordlist generator, result parser.
MITRE ATT&CK: T1595 (Active Scanning)
"""
import argparse, json, os, re, signal, subprocess, sys, textwrap
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
"quiet": {"rate": 30, "threads": 2},
"moderate": {"rate": 100, "threads": 10},
"loud": {"rate": 200, "threads": 40},
}
def _rate_flags(profile="moderate"):
    return RATE_FLAGS.get(profile, RATE_FLAGS["moderate"])

WL = {
"directories":["admin","api","backup","config","css","data","dev","dist","downloads","error","etc","files","git","health","images","inc","include","js","json","lib","login","logout","logs","old","panel","php","private","public","rest","scripts","search","secret","secure","server-status","sitemap.xml","sql","src","static","status","swagger","temp","test","tmp","uploads","vendor","web","wp-admin","wp-content","xml"],
"subdomains":["admin","api","app","blog","cdn","chat","cms","dashboard","db","dev","download","email","ftp","git","help","info","internal","jenkins","login","mail","manage","media","old","panel","portal","prod","sandbox","secure","shop","stage","staging","static","status","support","test","vpn","web","webmail","wiki","www"],
"parameters":["id","user","username","email","token","key","apikey","api_key","secret","pass","password","q","query","search","page","offset","limit","sort","filter","type","category","callback","redirect","url","file","path","action","debug","cmd","exec","code","dest","target","format","method"],
"extensions":[".php",".asp",".aspx",".jsp",".do",".action",".js",".json",".xml",".html",".htm",".txt",".pdf",".zip",".tar.gz",".sql",".bak",".old",".env",".config",".inc"],
"api_endpoints":["/api/users","/api/auth","/api/login","/api/admin","/api/config","/api/status","/api/health","/api/metrics","/api/logs","/api/v1/users","/api/v1/auth","/api/v2/users","/api/docs","/api/swagger","/api/graphql","/api/rest","/api/search","/api/upload","/api/export","/api/backup"],
"lfi_payloads":["../../etc/passwd","../../../etc/passwd","../../../../etc/passwd","../etc/passwd%00","....//....//etc/passwd","php://filter/convert.base64-encode/resource=index.php","/etc/passwd","/proc/self/environ"],
"common_files":["index.php","index.html","default.aspx","config.php","config.php.bak","config.php~",".htaccess",".htpasswd",".git/config",".env","composer.json","package.json","Dockerfile","Makefile","README.md","robots.txt","sitemap.xml","web.config","nginx.conf",".DS_Store"],
}

def which(cmd):
    for p in os.environ.get("PATH","").split(os.pathsep):
        for e in ("",".exe"):
            fp=os.path.join(p,cmd+e)
            if os.path.isfile(fp) and os.access(fp,os.X_OK): return fp
    return None

def gen_wl(name,typ,extra=None):
    w=list(WL.get(typ,[]))
    if extra: w.extend(extra)
    seen=set();u=[]
    for x in w:
        if x not in seen: seen.add(x);u.append(x)
    fp=f"wl_{name}_{typ}.txt"
    with open(fp,"w") as f: f.write("\n".join(u)+"\n")
    print(f"{Fore.GREEN}[+] {fp} ({len(u)} entries){Style.RESET_ALL}")
    return fp

def build_cmd(url,wl,opts):
    c=["ffuf"]
    c.extend(["-u",url if "{FUZZ}" in url else url+"FUZZ"])
    c.extend(["-w",wl])
    if opts.get("output"): c.extend(["-o",opts["output"],"-of","json"])
    for f in ("fc","fs","fw","fl"):
        if opts.get(f): c.extend(["-"+f,str(opts[f])])
    for m in ("mc","ms"):
        if opts.get(m): c.extend(["-"+m,str(opts[m])])
    c.extend(["-t",str(opts.get("threads",40))])
    if opts.get("rate"): c.extend(["-rate",str(opts["rate"])])
    if opts.get("timeout"): c.extend(["-timeout",str(opts["timeout"])])
    if opts.get("delay"): c.extend(["-p",str(opts["delay"])])
    for h in opts.get("headers",[]): c.extend(["-H",h])
    if opts.get("cookie"): c.extend(["-b",opts["cookie"]])
    if opts.get("proxy"): c.extend(["-x",opts["proxy"]])
    if opts.get("recursion"): c.extend(["-recursion"])
    if opts.get("recursion_depth"): c.extend(["-recursion-depth",str(opts["recursion_depth"])])
    if opts.get("extensions"): c.extend(["-e",opts["extensions"]])
    if opts.get("ac"): c.append("-ac")
    if opts.get("quiet"): c.append("-s")
    return c

def run_ffuf(cmd):
    if not which("ffuf"): print(f"{Fore.RED}[!] ffuf not found{Style.RESET_ALL}"); return None
    print(f"\n{Fore.CYAN}[*] {' '.join(cmd)}{Style.RESET_ALL}\n")
    try:
        proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        for line in proc.stdout: print(line,end="")
        proc.wait()
        return proc.returncode
    except FileNotFoundError: print(f"{Fore.RED}[!] ffuf binary not found{Style.RESET_ALL}"); return None

def parse_json(jp):
    try:
        with open(jp) as f: data=json.load(f)
    except (FileNotFoundError,json.JSONDecodeError) as e: print(f"{Fore.RED}[!] {e}{Style.RESET_ALL}"); return None
    results=data.get("results",[])
    if not results: print(f"{Fore.YELLOW}[!] No results{Style.RESET_ALL}"); return []
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n{Fore.WHITE}{Style.BRIGHT} Results ({len(results)}){Style.RESET_ALL}\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    parsed=[]
    for r in sorted(results,key=lambda x:x.get("status",0)):
        st=r.get("status",0);ln=r.get("length",0);wd=r.get("words",0);url=r.get("url","");ct=r.get("content-type","")
        sc={2:Fore.GREEN,3:Fore.YELLOW,4:Fore.CYAN,5:Fore.RED}.get(st//100,Fore.WHITE)
        print(f"  {sc}[{st}]{Style.RESET_ALL} {url:<50} L:{ln} W:{wd} [{ct}]")
        parsed.append(r)
    return parsed

def main():
    p=argparse.ArgumentParser(description="ffuf Automation Tool")
    prof=p.add_mutually_exclusive_group()
    prof.add_argument("--quiet",dest="profile",action="store_const",const="quiet",help="Noise profile: rate 30, 2 threads (use before subcommand)")
    prof.add_argument("--moderate",dest="profile",action="store_const",const="moderate",help="Noise profile: rate 100, 10 threads (default)")
    prof.add_argument("--loud",dest="profile",action="store_const",const="loud",help="Noise profile: rate 200, 40 threads")
    p.set_defaults(profile="moderate")
    sp=p.add_subparsers(dest="cmd")
    # build
    bp=sp.add_parser("build",help="Build ffuf command")
    bp.add_argument("url");bp.add_argument("-w","--wordlist")
    bp.add_argument("--wordlist-type",choices=list(WL.keys()),default="directories")
    bp.add_argument("--wordlist-name",default="custom")
    bp.add_argument("--extra-words","-ew",nargs="+",default=[])
    for f in ("fc","fs","fw","fl"): bp.add_argument("-"+f,type=int,default=None)
    for m in ("mc","ms"): bp.add_argument("-"+m,type=str,default=None)
    bp.add_argument("-t","--threads",type=int,default=None);bp.add_argument("--rate",type=int,default=None)
    bp.add_argument("--timeout",type=int,default=10);bp.add_argument("--delay",type=str,default=None)
    bp.add_argument("-H","--header",action="append",default=[]);bp.add_argument("-b","--cookie")
    bp.add_argument("-x","--proxy");bp.add_argument("--recursion",action="store_true")
    bp.add_argument("--recursion-depth",type=int,default=2)
    bp.add_argument("--extensions","-e");bp.add_argument("--ac",action="store_true")
    bp.add_argument("-o","--output");bp.add_argument("-q","--quiet",action="store_true")
    bp.add_argument("--run",action="store_true")
    # wordlist
    wp=sp.add_parser("wordlist",help="Generate wordlist")
    wp.add_argument("type",nargs="?",default="list");wp.add_argument("--name",default="custom")
    wp.add_argument("--extra",nargs="+",default=[])
    # parse
    pp=sp.add_parser("parse",help="Parse ffuf JSON")
    pp.add_argument("json_file");pp.add_argument("-o","--output")
    a=p.parse_args()
    if not a.cmd: p.print_help(); return
    if a.cmd=="wordlist":
        if a.type=="list":
            print(f"\n{Fore.CYAN}Wordlist types:{Style.RESET_ALL}")
            for tid,words in WL.items(): print(f"  {Fore.GREEN}{tid}{Style.RESET_ALL} ({len(words)})")
        else: gen_wl(a.name,a.type,a.extra)
        return
    if a.cmd=="parse":
        parsed=parse_json(a.json_file)
        if parsed and a.output:
            with open(a.output,"w") as f: json.dump(parsed,f,indent=2)
            print(f"{Fore.GREEN}[+] {a.output}{Style.RESET_ALL}")
        return
    if a.cmd=="build":
        wl=a.wordlist or gen_wl(a.wordlist_name,a.wordlist_type,a.extra_words)
        rf=_rate_flags(a.profile)
        if a.threads is None: a.threads=rf["threads"]
        if a.rate is None: a.rate=rf["rate"]
        opts={k:getattr(a,k,None) for k in ("fc","fs","fw","fl","mc","ms","threads","rate","timeout","delay","header","cookie","proxy","recursion","recursion_depth","extensions","ac","output","quiet")}
        opts["headers"]=a.header
        cmd=build_cmd(a.url,wl,opts)
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n{Fore.WHITE}{Style.BRIGHT} ffuf Command{Style.RESET_ALL}\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n  {' '.join(cmd)}\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        if a.run:
            rc=run_ffuf(cmd)
            if rc is None: sys.exit(1)
            if a.output: parse_json(a.output)

if __name__ == "__main__":
    main()
