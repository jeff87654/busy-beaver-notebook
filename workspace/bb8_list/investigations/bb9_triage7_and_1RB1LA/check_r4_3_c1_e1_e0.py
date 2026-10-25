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

def trace_c1_e(label, tape, pos, q, max_steps=400):
    print(f"\n=== {label} ===")
    for st in range(1, max_steps + 1):
        c = tape.get(pos, 0)
        slot = chr(65+q) + str(c)
        if slot in ('C1', 'E0', 'E1'):
            lo = min(list(tape.keys()) + [pos]) - 2
            hi = max(list(tape.keys()) + [pos]) + 2
            s = ''.join(f"[{slot}]" if i == pos else str(tape.get(i, 0)) for i in range(lo, hi + 1))
            print(f"  st {st:3d} ({slot}): {s}")
        if (q, c) not in tr:
            print(f"  HALT at st {st} ({slot})")
            break
        W, d, nq = tr[(q, c)]
        if W: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d; q = nq
        if q == 1 and tape.get(pos, 0) == 0 and tape and pos > max(tape.keys()):
            lo = min(tape.keys())
            ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
            parts = ww.split('10')
            if len(parts) >= 2 and not any(set(x) - {'1'} for x in parts) and len(parts[-1]) == 1:
                vals = [len(x) for x in parts[:-1]]
                print(f"  Reached K({vals[:-1]}; {vals[-1]}) at st {st}")
                if st > 20:
                    break

trace_c1_e("Blank -> K(3, 1; 14)", {}, 0, 0, max_steps=250)

for label, ds, a in [
    ("[0, 0; 3] (Epoch 1 rebuild)", [0, 0], 3),
    ("[3, 0, 0; 3] (Epoch 2 halt)", [3, 0, 0], 3),
    ("[0; 2] (1-digit zero halt)", [0], 2),
    ("[0; 3] (1-digit zero rebuild)", [0], 3),
]:
    w = kl.word(t, ds, a, 0)
    tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
    trace_c1_e(label, tape, len(w), 1, max_steps=400)
