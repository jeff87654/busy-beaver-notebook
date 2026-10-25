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

# Let's trace C1 = 0LB and 1LF on k=1..25 (with N=10) and print the exact formula for (ds, a, b)!
tr = list(tr_base)
tr[2*2 + 1] = "1LF"

print("=== C1 = 1LF for k = 1..25 (with N = 10) ===")
for k in range(1, 26):
    N = 10
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
            print(f"  k={k:2d}: len={len(ds_out)}, ds={ds_out}, a={a_out}, b={b_out} @{step}")
            break
    else:
        print(f"  k={k:2d}: TIMEOUT")

# Also let's print the first 60 steps of C1 = 1LF on k = 3, N = 5 to see HOW it eats (10)^{2k-1}!
print("\n=== Step-by-step trace of C1 = 1LF on k = 3, N = 4 ===")
k, N = 3, 4
left_str = "10"*(2*k-1) + "11001"
right_str = "100" + "1100"*N + "1"
full_str = left_str + "1" + right_str
h0 = len(left_str)
tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
h, s = h0, 2
for step in range(1, 700):
    b = tape.get(h, 0)
    if step <= 30 or s == 4 and b == 0:
        ones = [i for i, v in tape.items() if v == 1]
        mn, mx = min(min(ones), h), max(max(ones), h)
        cfg = "".join(f"[{chr(65+s)}{tape.get(i,0)}]" if i == h else str(tape.get(i,0)) for i in range(mn, mx+1))
        print(f"  st {step:3d}: {cfg}")
    act = tr[2*s + b]
    if int(act[0]): tape[h] = 1
    else: tape.pop(h, None)
    h += 1 if act[1] == "R" else -1
    s = ord(act[2]) - 65
    if parse_K_tape(tape, h, s) is not None:
        ones = [i for i, v in tape.items() if v == 1]
        mn, mx = min(min(ones), h), max(max(ones), h)
        cfg = "".join(f"[{chr(65+s)}{tape.get(i,0)}]" if i == h else str(tape.get(i,0)) for i in range(mn, mx+1))
        print(f"  st {step:3d} (CLEAN K!): {cfg}")
        break
