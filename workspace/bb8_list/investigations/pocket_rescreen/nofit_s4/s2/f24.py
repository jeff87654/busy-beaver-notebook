import sys,re
from val import probe
m='1RB1RA_0LC0RG_1LE1LD_1LC0LB_0RF1RD_1RB1RD_1RE0RH_1RA---'
def enc(j,L): return 'F 001'+'010'*j+'0'+''.join('01'*a+'0' for a in L)+'|0'
def dec(r):
    if r[0]!='S': return (r[0],r[1])
    if r[4].strip('0'): return ('R?',)
    t=r[2].lstrip('0')
    g=re.fullmatch(r'1((?:010)*)0((?:(?:01)*0)*)',t)
    if not g: return ('?',re.sub(r'(01)+',lambda q:'(01)^%d '%(len(q.group(0))//2),t)[:120])
    L=[len(b)//2 for b in g.group(2)[:-1].split('0')] if g.group(2) else []
    # blocks separated by single 0: split on '0' after (01)*: careful, use regex
    L=[len(b)//2 for b in re.findall(r'((?:01)*)0',g.group(2))]
    return (len(g.group(1))//3,L)
def run(j,L,n,quiet=False,filt=None):
    cf=enc(j,L); out=[]
    for k in range(n):
        r=probe(m,'F','R',[cf],10**10)[0]
        d=dec(r)
        if not quiet and (filt is None or filt(d)): print(k,r[1],d)
        out.append(d)
        if r[0]!='S': break
        cf='F '+r[2]+'|'+r[4]
    return out
if __name__=='__main__':
    j=int(sys.argv[1]); L=list(map(int,sys.argv[2].split(','))) if sys.argv[2] else []; n=int(sys.argv[3])
    run(j,L,n)
