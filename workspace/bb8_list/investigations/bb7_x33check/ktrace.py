import idle, sys
from sim import *
m = {"X":X,"I":I}.get(sys.argv[1], sys.argv[1])
N = int(sys.argv[2])
def code(tape, pos):
    ones = [k for k in tape if tape[k]]
    lo = min(ones)
    s = ''.join(str(tape.get(i,0)) for i in range(lo, pos))
    return [len(p) for p in s.split('0')]
def comp(L):
    out=[]; 
    for v in L:
        if out and out[-1][0]==v: out[-1][1]+=1
        else: out.append([v,1])
    return ','.join(str(v) if c==1 else f'{v}^{c}' for v,c in out)
def show(n, tape, pos, st):
    if st == 0 and tape.get(pos,0)==0 and pos > max(k for k in tape if tape[k]):
        print(n, comp(code(tape,pos)))
r = run(m, N, show)
print(r[:5])
