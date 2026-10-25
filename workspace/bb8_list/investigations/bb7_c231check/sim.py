import idle
M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
M2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"
def parse(m):
    T={}
    for s,row in enumerate(m.split('_')):
        for b in (0,1):
            t=row[3*b:3*b+3]
            T[(s,b)] = None if t[2] in '-Z' else (int(t[0]), 1 if t[1]=='R' else -1, ord(t[2])-65)
    return T
def show(tape,h,s):
    ks=[k for k,v in tape.items() if v] + [h]
    lo,hi=min(ks),max(ks)
    out=[]
    for i in range(lo,hi+1):
        c=str(tape.get(i,0))
        out.append(f"[{'ABCDEFG'[s]}{c}]" if i==h else c)
    return ''.join(out), lo
