import sys
from machines import *
from rsim import Sim
# print tape when entering a watched (state,sym) transition; compress (10)^n / (01)^n patterns
m = globals()[sys.argv[1]]; N = int(sys.argv[2]); watch = sys.argv[3].split(',')
def comp(runs):
    # runs: list of [sym,cnt] left->right; tokens: 1^n blocks with single-0 separators
    out=[]; 
    for s,n in runs: out.append(f"{s}^{n}" if n>1 else str(s))
    # collapse repeated "0 1" pairs
    res=[]; i=0
    while i < len(out):
        j=i; k=0
        while j+1 < len(out) and out[j]=='0' and out[j+1]=='1': j+=2; k+=1
        if k>=2: res.append(f"(01)^{k}"); i=j
        else: res.append(out[i]); i+=1
    return ' '.join(res)
s = Sim(m); last=None
for i in range(N):
    if s.halted: print('HALT', s.steps); break
    src = s.R if s.face=='R' else s.L; sym = src[-1][0] if src else 0
    if f"{s.st}{sym}" in watch:
        head = f"<{s.st}" if s.face=='L' else f"{s.st}>"
        print(f"{s.steps:>12} {comp(s.L)} {head} {comp(list(reversed(s.R)))}"[:400], flush=True)
    s.step()
print('end steps', s.steps, 'state', s.st)
