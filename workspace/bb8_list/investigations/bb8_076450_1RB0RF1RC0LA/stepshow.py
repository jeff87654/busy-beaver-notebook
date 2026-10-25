import sys, re
TM = "1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF"
T = {}
for qi, ch in enumerate(TM.split('_')):
    for s in (0,1):
        e = ch[3*s:3*s+3]
        T[('ABCDEFGH'[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1]=='R' else -1, e[2])
def expand(w): return re.sub(r'\(([01]+)\)\^(\d+)', lambda m: m.group(1)*int(m.group(2)), w).replace(' ','')
def show(tape, pos, st):
    lo = min(k for k in tape if tape[k] or k==pos); hi = max(k for k in tape if tape[k] or k==pos)
    return ''.join(('['+st+str(tape.get(i,0))+']') if i==pos else str(tape.get(i,0)) for i in range(lo, hi+1))
w = expand(sys.argv[1]); st = sys.argv[2]; pos = int(sys.argv[3]); n = int(sys.argv[4])
tape = {i:int(c) for i,c in enumerate(w)}
for i in range(n+1):
    print(i, show(tape,pos,st))
    e = T[(st, tape.get(pos,0))]
    if e is None: print('HALT'); break
    tape[pos] = e[0]; pos += e[1]; st = e[2]
