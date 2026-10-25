# Run literally from a word until a predicate on (state, tape, pos) holds; print the last K configs.
import sys, re, collections
TM = "1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF"
T = {}
for qi, ch in enumerate(TM.split('_')):
    for s in (0,1):
        e = ch[3*s:3*s+3]
        T[('ABCDEFGH'[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1]=='R' else -1, e[2])
def expand(w): return re.sub(r'\(([01]+)\)\^(\d+)', lambda m: m.group(1)*int(m.group(2)), w).replace(' ','')
def show(tape, pos, st, lo, hi):
    return ''.join(('['+st+str(tape.get(i,0))+']') if i==pos else str(tape.get(i,0)) for i in range(lo, hi+1))
w = expand(sys.argv[1]); st = sys.argv[2]; pos = int(sys.argv[3]); target = re.compile(sys.argv[4]); K = int(sys.argv[5])
tape = {i:int(c) for i,c in enumerate(w)}
hist = collections.deque(maxlen=K)
steps = 0
lo, hi = -3, len(w)+3
while steps < 10**7:
    lo = min(lo, pos-2); hi = max(hi, pos+2)
    s = show(tape, pos, st, lo, hi).strip()
    hist.append((steps, s))
    # event: state at left edge
    left = [tape.get(i,0) for i in range(lo, pos)]
    if not any(left) and target.match(st + str(tape.get(pos,0)) + '|' + ''.join(str(tape.get(i,0)) for i in range(pos+1, hi+1)).rstrip('0')) and steps > 0:
        break
    e = T[(st, tape.get(pos,0))]
    if e is None: print('HALT'); break
    tape[pos] = e[0]; pos += e[1]; st = e[2]; steps += 1
for s in hist: print(s[0], s[1])
