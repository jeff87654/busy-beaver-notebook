import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
tr_base = [t for row in M1.split("_") for t in (row[:3], row[3:])]

def parse_K_tape(tape, h, s):
    if s != 4 or tape.get(h, 0) != 0:
        return None
    ones = [i for i, v in tape.items() if v == 1]
    if not ones or h >= min(ones):
        return None
    mn, mx = min(ones), max(ones)
    if h != mn - 1:
        return None
    rev_w = "".join(str(tape.get(i, 0)) for i in range(mn, mx + 1))
    w = rev_w[::-1]
    if not (w.startswith("100") and w.endswith("1")) or len(w) < 4:
        return None
    body = w[3:-1]
    parts = body.split("00")
    if len(parts) < 2:
        return None
    vals = []
    for p in parts:
        if len(p) % 2 != 0 or set(p) - {'1'}:
            return None
        vals.append(len(p) // 2)
    return (vals[:-2], vals[-2], vals[-1])

def trace_c1_detail(c1_act, h0_act, h1_act, k, N, max_steps=200):
    tr = list(tr_base) + [h0_act, h1_act]
    tr[2*2 + 1] = c1_act
    left_str = "10"*(2*k-1) + "11001"
    right_str = "100" + "1100"*N + "1"
    full_str = left_str + "1" + right_str
    h0 = len(left_str)
    tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
    h, s = h0, 2
    print(f"\n=== Detail: C1={c1_act}, H={h0_act}{h1_act}, k={k}, N={N} ===")
    for step in range(1, max_steps + 1):
        b = tape.get(h, 0)
        if step <= 35 or (s == 4 and b == 0) or s == 7:
            ones = [i for i, v in tape.items() if v == 1]
            mn, mx = min(min(ones), h), max(max(ones), h)
            cfg = "".join(f"[{chr(65+s)}{tape.get(i,0)}]" if i == h else str(tape.get(i,0)) for i in range(mn, mx+1))
            print(f"  st {step:4d}: {cfg}")
        act = tr[2*s + b]
        if act == "---":
            print(f"  HALT at step {step} on {chr(65+s)}{b}")
            break
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == "R" else -1
        s = ord(act[2]) - 65
        parsed = parse_K_tape(tape, h, s)
        if parsed is not None:
            print(f"  CLEAN K at step {step}: {parsed}")
            break

trace_c1_detail("1LH", "---", "0LD", k=1, N=4, max_steps=250)
