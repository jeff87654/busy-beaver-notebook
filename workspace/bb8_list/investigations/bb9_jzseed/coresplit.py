import sys, re, collections
CH='1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH'
CORE=[0,1,2,3,4,5,6,7,9,10,11,13]
def sl(m): return [m[7*q+3*c:7*q+3*c+3] for q in range(9) for c in range(2)]
cs=sl(CH); C=collections.Counter(); best=[]
for fn in sys.argv[1:]:
    for l in open(fn):
        if not l.startswith('R '): continue
        f=l.split(); s=sl(f[1]); intact=all(s[i]==cs[i] for i in CORE)
        k='intact' if intact else 'broken'; C[(k,f[3])]+=1
        if not intact and f[3]=='HALT':
            sig=re.search(r' sigma=(\S+)',l).group(1)
            if sig.isdigit(): best.append((int(sig),f[1],f[2]))
            else: best.append((10**40,f[1],f[2],sig))
for k in sorted(C): print(k, C[k])
best.sort(reverse=True)
for b in best[:8]: print('broken halter', b)
