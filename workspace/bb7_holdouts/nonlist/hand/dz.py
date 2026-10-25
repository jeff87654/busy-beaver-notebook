"""dz.py MACHINE K TAPE MAXMACRO [--every=N] [--tail=N] [--all]
TAPE: ms 'i' format line 'Q side | tok ...' (a file whose 2nd line is that, or literal string starting with 'X:').
Runs ms.exe, prints only tape-end events (head at an end) compressed with periods 1-4 (pattern)xN;
by default prints an event only when the tape with the last (head-side) 2 counts masked changes (skeleton+slow counts)."""
import re, subprocess, sys
args=[a for a in sys.argv[1:] if not a.startswith('--')]; opts=dict(a[2:].split('=') if '=' in a else (a[2:],'1') for a in sys.argv[1:] if a.startswith('--'))
m,K,tp,mm=args[:4]
line = tp[2:] if tp.startswith('X:') else open(tp).read().splitlines()[1]
MASK=int(opts.get('mask','2')); ALL='all' in opts
ms=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
p=subprocess.Popen([ms,m,K,mm,opts.get('mode','l0'),'i'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,creationflags=0x40)
p.stdin.write(line+'\n'); p.stdin.close()
def comp(ts):
    out=[];i=0
    while i<len(ts):
        best=None
        for per in (1,2,3,4):
            j=i
            while j+per<len(ts) and ts[j+per]==ts[j]: j+=1
            reps=(j-i)//per+1
            if reps>=3 and (best is None or reps*per>best[0]*best[1]): best=(reps,per)
        if best: r,per=best; out.append('('+' '.join(ts[i:i+per])+')x%d'%r); i+=r*per
        else: out.append(ts[i]); i+=1
    return ' '.join(out)
prev=None
lastp=0
import atexit; atexit.register(lambda: p.kill())
for l in p.stdout:
    if not l.startswith('T '): print(l.strip()); continue
    a,b=l.split('|',1); t=b.split(); 
    if not(t[0].startswith('[') or t[-1].startswith('[')): continue
    # orient: head side first
    if t[-1].startswith('['): t=t[::-1]; side='R'
    else: side='L'
    t=[x for x in t[1:]]
    c=comp(t).replace('^1 ',' ')
    toks=c.split(' ')
    key=(side+re.sub(r'\^\d+','^',c)) if 'skel' in opts else side+re.sub(r'\^\d+','^',' '.join(toks[:MASK]))+' '+' '.join(toks[MASK:])
    itn=int(a.split()[1])
    if 'geo' in opts:
        if itn < lastp*float(opts['geo']): continue
        lastp=max(itn,1); key=itn
    if ALL or key!=prev:
        sys.stdout.write(' '.join([a.split()[1],a.split()[2],a.split()[3],side,'|',c[:int(opts.get('w','230'))]])+chr(10)); sys.stdout.flush(); prev=key
        if 0: print(a.split()[1],a.split()[2],a.split()[3],side,'|',c[:int(opts.get('w','230'))]); prev=key
