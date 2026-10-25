# events.py FILE [w] : per "== label" block, the event sequence: J views with RLE expanded; a counter step (C X 1^k ->
# C-3 T 1^k) keeps the signature (tokens except the two before the trailing ones, k); print first view of each signature.
import sys, re
def blocks(fn):
    lab=None; cur=[]
    for l in open(fn):
        l=l.rstrip('\n')
        if l.startswith('== '):
            if lab: yield lab,cur
            lab=l[3:]; cur=[]
        else: cur.append(l)
    if lab: yield lab,cur
def expand(v):
    out=[]
    for x in v.split():
        if '*' in x: a,n=x.split('*'); out+= [a]*int(n)
        else: out.append(x)
    return out
def sig(t):
    k=0
    while k<len(t) and t[-1-k]=='1': k+=1
    head=t[:len(t)-k]
    return (tuple(head[:-2]), k)
def ev(lines):
    out=[]; prev=None; end=''
    for l in lines:
        if l.startswith('J'):
            t=expand(l.partition('|')[2]); s=sig(t)
            if s!=prev: out.append(t); prev=s
        elif l.split()[:1] in (['HALT'],['STOP'],['END']): end=' '.join(l.split()[:2])
    return out,end
def show(t):
    k=0
    while k<len(t) and t[-1-k]=='1': k+=1
    s=[]; i=0; h=t[:len(t)-k]
    while i<len(h):
        j=i
        while j<len(h) and h[j]==h[i]: j+=1
        s.append(h[i] if j-i==1 else '%s*%d'%(h[i],j-i)); i=j
    return ' '.join(s)+(' |%d'%k)
if __name__=='__main__':
    w=int(sys.argv[2]) if len(sys.argv)>2 else 0
    for lab,ls in blocks(sys.argv[1]):
        e,end=ev(ls); print('==',lab,len(e),end)
        if w:
            for x in e: print('   ',show(x)[-w:])
