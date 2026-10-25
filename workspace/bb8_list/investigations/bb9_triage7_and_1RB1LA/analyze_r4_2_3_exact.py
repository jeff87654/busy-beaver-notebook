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

print("=== Grid of [y, 0, 0; a] for y=0..5, a=0..7 ===")
for y in range(6):
    row = []
    for a in range(8):
        ds = [0, 0] if y == 0 else [y, 0, 0]
        tape, pos, q = make_s10(ds, a, 0)
        kind, st, k, used = trace_tm(tm, tape, pos, q, max_steps=50000, stop_fn=check_s10)
        if kind == 'H':
            row.append(f"H({k})")
        elif kind == 'K':
            d_out, a_out = k
            # compress d_out
            row.append(f"{d_out};{a_out}")
        else:
            row.append("T")
    print(f"y={y}: " + " | ".join(f"{x:22s}" for x in row))

print("\n=== Grid of [z, y, 0, 0; a] for z=3, y=1..3, a=0..3 ===")
for y in range(1, 4):
    row = []
    for a in range(4):
        tape, pos, q = make_s10([3, y, 0, 0], a, 0)
        kind, st, k, used = trace_tm(tm, tape, pos, q, max_steps=50000, stop_fn=check_s10)
        if kind == 'H':
            row.append(f"H({k})")
        elif kind == 'K':
            d_out, a_out = k
            row.append(f"{d_out};{a_out}")
        else:
            row.append("T")
    print(f"[3,{y},0,0]: " + " | ".join(f"{x:26s}" for x in row))
