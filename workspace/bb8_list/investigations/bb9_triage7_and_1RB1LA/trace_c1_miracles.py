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

# 1. Check whether D and Bk EVER step left of the leftmost '1' of "100 (11)^a 00 ..."!
print("=== 1. Check minimum head position during D and Bk on K(ds; a; 0) ===")
for label, rev_w in [
    ("D: K(1, 2; 3; 0)", "100" + "11"*3 + "00" + "11"*2 + "00" + "11"*1 + "00" + "1"),
    ("B1: K(1, 0; 3; 0)", "100" + "11"*3 + "00" + "" + "00" + "11"*1 + "00" + "1"),
    ("B2: K(1, 0, 0; 3; 0)", "100" + "11"*3 + "00" + "00"*2 + "11"*1 + "00" + "1"),
]:
    tape = {i: int(c) for i, c in enumerate(rev_w) if c == '1'}
    h, s = -1, 4 # [E0] at index -1
    min_h = h
    for step in range(1, 10000):
        b = tape.get(h, 0)
        act = tr_base[2*s + b]
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == "R" else -1
        s = ord(act[2]) - 65
        if h < min_h:
            min_h = h
        if parse_K_tape(tape, h, s) is not None:
            print(f"  {label:22s}: finished at step {step:4d}, min_h = {min_h}")
            break

# 2. Trace C1 = 0LB intermediate K-like states from (10)^{2k-1} 1100 1 [C1] 100 (1100)^N 1
print("\n=== 2. How C1 = 0LB (and 1LF, 1RC, 1RF) eats the left prefix (10)^{2k-1} 1100 1 ===")
tr = list(tr_base)
tr[2*2 + 1] = "0LB"
for k in [1, 2, 3, 4, 5, 20]:
    N = 25 if k == 20 else 6
    left_str = "10"*(2*k-1) + "11001"
    right_str = "100" + "1100"*N + "1"
    full_str = left_str + "1" + right_str
    h0 = len(left_str)
    tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
    h, s = h0, 2
    for step in range(1, 200000):
        b = tape.get(h, 0)
        act = tr[2*s + b]
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == "R" else -1
        s = ord(act[2]) - 65
        parsed = parse_K_tape(tape, h, s)
        if parsed is not None:
            ds_out, a_out, b_out = parsed
            print(f"  0LB k={k:2d}, N={N:2d} -> CLEAN K(len={len(ds_out)}, ds=..{ds_out[-5:]}; a={a_out}; b={b_out}) @{step}")
            break

# 3. Check C1 = 1LC and 1LD WITHOUT breaking on KP (wait for CLEAN K)!
print("\n=== 3. C1 = 1LC and 1LD waiting for CLEAN K (up to 500,000 steps) ===")
for cand in ["1LC", "1LD", "0LF", "0LD", "0RA", "1LA"]:
    tr = list(tr_base)
    tr[2*2 + 1] = cand
    row = []
    for k in range(1, 9):
        N = 5
        left_str = "10"*(2*k-1) + "11001"
        right_str = "100" + "1100"*N + "1"
        full_str = left_str + "1" + right_str
        h0 = len(left_str)
        tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
        h, s = h0, 2
        res = "T"
        for step in range(1, 300000):
            b = tape.get(h, 0)
            act = tr[2*s + b]
            if int(act[0]): tape[h] = 1
            else: tape.pop(h, None)
            h += 1 if act[1] == "R" else -1
            s = ord(act[2]) - 65
            parsed = parse_K_tape(tape, h, s)
            if parsed is not None:
                ds_out, a_out, b_out = parsed
                res = f"CLEAN(len={len(ds_out)},a={a_out},b={b_out})@{step}"
                break
        row.append(f"k={k}:{res}")
    print(f"  {cand}: " + " | ".join(row))
