from canon import *
import collections,sys,re
kL=int(sys.argv[2]);kG=int(sys.argv[3]);CAP=int(sys.argv[4])
def gtok(G):
    out=[];i=0
    while i<len(G):
        if G[i]==2:
            j=i
            while j<len(G) and G[j]==2: j+=1
            out.append('D');i=j
        else:
            out.append(str(G[i]) if G[i]<=CAP else 'B'); i+=1
    out.append('$')
    return out
def ltok(L):
    s=''.join(map(str,L)).lstrip('0')
    s=re.sub(r'(110)+','T',s)
    return list(reversed(['$']+list(s)))
L=[];P='01';G=[2]*3
V=collections.Counter()
for i in range(int(sys.argv[1])):
    V[(tuple(ltok(L)[:kL]),P,tuple(gtok(G)[:kG]))]+=1
    L,P,G=step(L,P,G)
print(len(V))
