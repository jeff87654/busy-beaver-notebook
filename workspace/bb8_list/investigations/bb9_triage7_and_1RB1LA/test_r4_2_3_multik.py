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

for ds, a in [
    ([3, 1, 0, 0], 0),
    ([3, 2, 0, 0], 0),
    ([3, 2, 2, 0, 0], 0),
    ([3, 2, 2, 1, 0, 0], 0),
    ([3, 2, 1], 14),
    ([3, 2, 2, 1], 14),
    ([3, 2, 2, 2, 1], 14),
    ([3, 2, 2, 2, 2, 1], 14),
]:
    tape, pos, q = make_s10(ds, a, 0)
    kind, st, k, used = trace_tm(tm, tape, pos, q, max_steps=200000, stop_fn=check_s10)
    print(f"{str(ds)+';'+str(a):25s} -> {kind} {str(k):30s} ({st:6d} st) | C1={'C1' in used!s:5s} E1={'E1' in used!s:5s}")

# Let's trace multiple K-steps starting from [3, 2, 1; 14] and [3, 2, 2, 1; 2] and [3, 2, 2; 2]!
for start_ds, start_a in [
    ([3, 2, 1], 14),
    ([3, 2, 1], 2),
    ([3, 2, 2], 2),
]:
    print(f"\n--- Multi-K-step trace from {start_ds}; {start_a} ---")
    ds, a = list(start_ds), start_a
    for step_k in range(1, 30):
        tape, pos, q = make_s10(ds, a, 0)
        kind, st, k, used = trace_tm(tm, tape, pos, q, max_steps=500000, stop_fn=check_s10)
        print(f"  K-step {step_k:2d}: {str(ds)+';'+str(a):30s} -> {kind} {str(k):30s} ({st} st, C1={'C1' in used}, E1={'E1' in used})")
        if kind != 'K':
            break
        ds, a = k
        if any(x > 50 for x in ds) or a > 500:
            break
