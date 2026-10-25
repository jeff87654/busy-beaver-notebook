import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from test_r4_2_3_and_v_coding import trace_tm

tm = '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA1RB'
t = kl.tmpl(tm, 'R,B,P=-,u=1,s=10,d=1d+0,b=3b+1,S=-')

def make_s10(ds, a, b=0):
    w = kl.word(t, ds, a, b)
    tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
    return tape, len(w), 1

def check_s10(st, tape, pos, q):
    if q != 1 or tape.get(pos, 0) != 0:
        return None
    if not tape or pos <= max(tape.keys()):
        return None
    lo = min(tape.keys())
    ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
    parts = ww.split('10')
    if len(parts) < 2 or any(set(x) - {'1'} for x in parts):
        return None
    if len(parts[-1]) != 1:
        return None
    vals = [len(x) for x in parts[:-1]]
    return (vals[:-1], vals[-1])

for ds in [
    [3, 2, 0, 0],
    [3, 1, 0, 0],
    [3, 0, 0],
    [2, 0, 0],
    [1, 0, 0],
    [3, 2, 2, 0, 0],
    [3, 2, 1, 0, 0],
    [3, 2, 0, 0, 0],
    [3, 1, 0, 0, 0],
]:
    row = []
    for a in range(4):
        tape, pos, q = make_s10(ds, a, 0)
        kind, st, k, used = trace_tm(tm, tape, pos, q, max_steps=50000, stop_fn=check_s10)
        c1e1 = ('C' if 'C1' in used else '-') + ('E' if 'E1' in used else '-')
        if kind == 'H':
            row.append(f"H({k})[{c1e1}]")
        else:
            row.append(f"{k[0]};{k[1]}[{c1e1}]")
    print(f"{str(ds):18s}: " + " | ".join(f"{x:26s}" for x in row))
