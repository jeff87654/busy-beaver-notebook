import idle, subprocess, random, sys
X = "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE"
I = "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA0LG_---0LE"
def norm(ds):
    i=0
    while i<len(ds) and ds[i]==0: i+=1
    return ds[i:]
def predict(ds, b):
    ds = norm(list(ds))
    if not ds:
        if b%2: return ('HALT', b+3)
        return ('K', norm([2,1]+[2]*(b//2)), 1)
    if ds[-1] >= 1:
        return ('K', norm(ds[:-1]+[ds[-1]-1]), b+3)
    k=0
    while ds[-1-k]==0: k+=1
    y = ds[-1-k]-1
    return ('K', norm(ds[:-1-k]+[y, b-2*k+4]+[2]*(k-1)), 1)
def literal(m, cfgs, maxs=10**8):
    inp = ''.join(f"{len(ds)} {' '.join(map(str,ds))} {b}\n" for ds,b in cfgs)
    p = subprocess.run(['./lit.exe', m, str(maxs)], input=inp, capture_output=True, text=True, creationflags=0x40)
    out=[]
    for line in p.stdout.strip().split('\n'):
        f=line.split()
        if f[0]=='K':
            n=int(f[4]); v=list(map(int,f[5:])); out.append(('K', norm(v[:n]), v[n], int(f[1])))
        else: out.append((f[0], int(f[2]), f[3], int(f[1])))
    return out
