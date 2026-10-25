import idle, sys, subprocess, os, re
from evlog2 import rruns, pcomp
HERE=os.path.dirname(os.path.abspath(__file__))
def expand(tok):
    m=re.fullmatch(r'\((.*)\)x(\d+)',tok)
    if m: return expand_seq(m.group(1))*int(m.group(2))
    m=re.fullmatch(r'([01])(?:\^(\d+))?',tok)
    return m.group(1)*int(m.group(2) or 1)
def expand_seq(s):
    return ''.join(c*int(n or 1) for c,n in re.findall(r'([01])(?:\^(\d+))?',s))
def snapshot(M,step,side):
    p=subprocess.Popen([os.path.join(HERE,'ev.exe'),M,str(step+10**7),'1000000000000',side,'1'],stdout=subprocess.PIPE,text=True,creationflags=0x40)
    with open(os.path.join(HERE,'..','pids.txt'),'a') as f: f.write('%d ev.exe\n'%p.pid)
    for l in p.stdout:
        if '|' not in l: continue
        st=int(l.split()[0])
        if st>=step:
            p.kill(); h,r=l.split('|'); return h.split(), pcomp(rruns(r))
    return None,None
if __name__=='__main__':
    M,step,side=sys.argv[1:4]
    h,s=snapshot(M,int(step),side); print(h); print(s)
