import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl

tm = '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA1RB'
t = kl.tmpl(tm, 'R,B,P=-,u=1,s=10,d=1d+0,b=3b+1,S=-')
tr = {}
for qi, row in enumerate(tm.split('_')):
    for c in range(2):
        x = row[3*c:3*c+3]
        if x[0] != '-':
            tr[(qi, c)] = (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)

def inspect_halt_tape(ds, a):
    w = kl.word(t, ds, a, 0)
    tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
    pos, q = len(w), 1
    for st in range(1, 100000):
        c = tape.get(pos, 0)
        if (q, c) not in tr:
            lo = min( min(tape.keys()), pos )
            hi = max( max(tape.keys()), pos )
            s = ''
            for i in range(lo, hi + 1):
                if i == pos:
                    s += f"[{chr(65+q)}{tape.get(i, 0)}]"
                else:
                    s += str(tape.get(i, 0))
            print(f"  {str(ds)+';'+str(a):15s} halts at step {st:4d} (pos={pos}, lo={lo}, hi={hi}): {s}")
            return
        W, d, nq = tr[(q, c)]
        if W: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d; q = nq

print("=== Tape at E0 halt for [3, 0, 0; 4m+3] and [0, 0; 4m] ===")
for ds, a in [
    ([0, 0], 0),
    ([0, 0], 4),
    ([0, 0], 8),
    ([3, 0, 0], 3),
    ([3, 0, 0], 7),
    ([3, 0, 0], 11),
]:
    inspect_halt_tape(ds, a)

# Compare with non-halting [0, 0; 5] right before it finishes rebuild!
w = kl.word(t, [0, 0], 5, 0)
tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
pos, q = len(w), 1
for st in range(1, 1000):
    c = tape.get(pos, 0)
    W, d, nq = tr[(q, c)]
    if W: tape[pos] = 1
    else: tape.pop(pos, None)
    pos += d; q = nq
    if q == 4: # state E
        lo, hi = min(min(tape.keys()), pos), max(max(tape.keys()), pos)
        s = ''.join(f"[E{tape.get(i,0)}]" if i == pos else str(tape.get(i,0)) for i in range(lo, hi+1))
        print(f"  [0,0];5 at step {st:3d} in state E: {s}")
