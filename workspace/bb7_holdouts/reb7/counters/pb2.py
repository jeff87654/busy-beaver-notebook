import idle, sys, re
from thr import rlg
# raw-bit moments (mode 4: when last run before acc is 0 ; mode 3: all) parsed into u=10 runs with separators '0' (s) or '|' (alt sep '1')
def unrle(s):
    out=[]
    for tok in s.strip('.').split('.'):
        if not tok: continue
        if '^' in tok: c,n=tok.split('^'); out.append(c*int(n))
        else: out.append(tok)
    return ''.join(out)
SS='1'
def parse(bits):
    # strip trailing S
    assert bits.endswith(SS); b=bits[:len(bits)-len(SS)]
    toks=[]; i=0; cur=0; seps=[]; runs=[]
    while i<len(b):
        if b.startswith('10',i): cur+=1; i+=2
        elif b[i]=='0': runs.append(cur); seps.append(' '); cur=0; i+=1
        else: runs.append(cur); seps.append('|'); cur=0; i+=1
    runs.append(cur)
    o=str(runs[0])
    for s,r in zip(seps,runs[1:]): o+=s+str(r)
    # compress repeats
    return o
def comp(o):
    t=o.replace('|',' | ').split(' ')
    out=[];i=0
    while i<len(t):
        j=i
        while j<len(t) and t[j]==t[i]: j+=1
        out.append(t[i]+('x%d'%(j-i) if j-i>1 and t[i]!='|' and t[i]!='' else '')); i=j
    return ' '.join(x for x in out if x!='')
def show(M,O,Q,inp,N=10**8,mo=5,mode=4):
    res=[]
    for l in rlg(M,O,Q,'10','0',SS if SS else '-',inp,N,mo,mode):
        if '|' in l:
            st,bits=l.split('|',1); bits=unrle(bits.strip())
            res.append(st.strip()+' : '+comp(parse(bits)))
        else: res.append(l)
    return res
if __name__=='__main__':
    M,O,Q=sys.argv[1:4]; mo=int(sys.argv[4]); mode=int(sys.argv[5]); N=int(sys.argv[6]) if len(sys.argv)>6 else 10**8
    if len(sys.argv)>7: SS='' if sys.argv[7]=='-' else sys.argv[7]
    for line in sys.stdin:
        line=line.strip()
        if not line: continue
        print('>>',line)
        for l in show(M,O,Q,line,N,mo,mode): print('   ',l[:200])
