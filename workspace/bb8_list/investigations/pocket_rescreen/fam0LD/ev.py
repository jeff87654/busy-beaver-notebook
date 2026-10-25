import sys
def rl(s):
    if s=='-': return '-'
    xs=s.split(','); out=[]; i=0
    while i<len(xs):
        j=i
        while j<len(xs) and xs[j]==xs[i]: j+=1
        out.append(xs[i]+('^%d'%(j-i) if j-i>1 else '')); i=j
    return ' '.join(out)
prev=None
for line in open(sys.argv[1]):
    p=line.split()
    if p[0]!='K': continue
    ds,a,b=p[2],int(p[3]),int(p[4])
    if prev and not (prev[0]==ds and a==prev[1]-1 and b==prev[2]+2):
        print(rl(prev[0]),prev[1],prev[2],' -> ',rl(ds),a,b)
    prev=(ds,a,b)
