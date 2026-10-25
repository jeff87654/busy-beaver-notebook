# C(d; xs; a) = (10)^d [0 1^x]* 0 1^a 0 <H>0 ; next round-start event (word ending '100') parsed
import sys, re, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen'); import idle
from val import V
M=None
def word(d,xs,a): return '10'*d+''.join('0'+'1'*x for x in xs)+'0'+'1'*a+'0'
def parse(w):
    m=re.fullmatch(r'((?:10)*)((?:01*)*?)0(1+)00',w)
    if not m: return None
    xs=[len(t) for t in m.group(2).split('0')[1:]] if m.group(2) else []
    return (len(m.group(1))//2, tuple(xs), len(m.group(3)))
def nxt(machine, cfgs, maxs=4000000000):
    inp=''.join(f"H {word(d,xs,a).lstrip('0') or '-'} - [01]*100\n" for d,xs,a in cfgs)
    out=subprocess.run([V,machine,'H','R',str(maxs)],input=inp,capture_output=True,text=True).stdout.split('\n')
    res=[]
    for o in out[:len(cfgs)]:
        p=o.split()
        if p[0]=='M': res.append(parse(p[3]) or ('X',p[3][:40]))
        else: res.append(o)
    return res
if __name__=='__main__':
    m=sys.argv[1]
    cf=[eval(s) for s in sys.argv[2:]]
    for c,r in zip(cf,nxt(m,cf)): print(c,'->',r)
