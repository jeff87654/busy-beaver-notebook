# chk_round.py M SIDE:STATE PREFIXSPEC PATTERN_REGEX(with one group) SPEC_TEMPLATE(%d) HIDX  nlist  formula
import sys,re,subprocess; sys.path.insert(0,'.'); from chk import TV
def nxt(M,side,state,spec,hidx,rx,steps=4000000000):
    p=subprocess.Popen([TV,M,str(steps),side,'1','1','100000000',state,str(hidx),spec],stdout=subprocess.PIPE,text=True)
    res=None
    for l in p.stdout:
      if l.startswith('HALT') or l.startswith('END') or l.startswith('TAPE'): res=l.strip()[:40]; break
      if '|' in l:
        c=l.split('|',1)[1].strip(); mm=re.fullmatch(rx,c)
        if mm: res=int(mm.group(1)); break
    p.kill(); return res
def run(M,side,state,tmpl,hidx,rx,ns,f):
    ok=bad=0; badl=[]
    for n in ns:
        r=nxt(M,side,state,tmpl%n,hidx,rx)
        if r==f(n): ok+=1
        else: bad+=1; badl.append((n,r))
    print(M,'ok',ok,'bad',bad,badl[:8]); sys.stdout.flush()
