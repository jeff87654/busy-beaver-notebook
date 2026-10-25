import sys, subprocess, os, re
sys.path.insert(0,'../tools')
from lit import D0, EXE, TMP
def raw_preESC(L,P,s,y,t):
    l='11'+''.join('10'*d+'1' for d in [9,13])[:-1]  # far l = 11 D9 D13
    S=D0(l,s,y,P,L,t); fs=os.path.join(TMP,'c%d.txt'%os.getpid()); open(fs,'w').write(S)
    o=subprocess.run([EXE,'@file:%s:B'%fs,'--kmom','--steps','3e8','--width','100000'],capture_output=True,text=True).stdout
    os.remove(fs)
    for ln in o.splitlines():
        if ln.startswith('K ') and ' 1 (10)^6 1 (10)^7 (110)^' in ln:  # the pre-ESC signature for key37
            body=ln.split('[B')[0].split(' ',2)[2]
            return body.strip()
    return None
def expand(s):
    out=[]
    for m in re.finditer(r'\(([01]+)\)\^(\d+)|([01]+)', s):
        if m.group(1): out.append((m.group(1),int(m.group(2))))
        else:
            for ch in m.group(3): out.append((ch,1))
    # flatten to cells
    cells=[]
    for blk,n in out:
        cells += [int(c) for c in blk]*n
    return cells
base=raw_preESC(38,24,3,8,2)
print('base raw:',base)
print('base cells len',len(expand(base)))
for lbl,(P,s,y,t) in [('P+6',(30,3,8,2)),('s+1',(24,4,8,2)),('y+1',(24,3,9,2)),('t+1',(24,3,8,3))]:
    c=raw_preESC(38,P,s,y,t); 
    print(lbl, 'dlen', len(expand(c))-len(expand(base)))
