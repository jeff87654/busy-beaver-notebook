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

for cand in ["0LB", "1LF", "1RC", "1RF", "1LC", "1LD", "0RD", "0RE", "0LF", "1LA", "1RD"]:
    print(f"\n=== C1 = {cand} (N = 3a+1-k = 6) ===")
    tr = list(tr_base)
    tr[2*2 + 1] = cand
    for k in range(1, 10):
        N = 6
        left_str = "10"*(2*k-1) + "11001"
        right_str = "100" + "1100"*N + "1"
        full_str = left_str + "1" + right_str
        h0 = len(left_str)
        tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
        h, s = h0, 2
        outcome = "T"
        for step in range(1, 50000):
            b = tape.get(h, 0)
            act = tr[2*s + b]
            if int(act[0]): tape[h] = 1
            else: tape.pop(h, None)
            h += 1 if act[1] == "R" else -1
            s = ord(act[2]) - 65
            parsed = parse_K_tape(tape, h, s)
            if parsed is not None:
                ds_out, a_out, b_out = parsed
                outcome = f"CLEAN K(len={len(ds_out)}, ds={ds_out}; a={a_out}; b={b_out}) @{step}"
                break
            if s == 4 and tape.get(h, 0) == 0 and tape.get(h+1, 0) == 1 and tape.get(h+2, 0) == 0 and tape.get(h+3, 0) == 0:
                ones = [i for i, v in tape.items() if v == 1]
                left_ones = [i for i in ones if i < h]
                if left_ones:
                    l_str = "".join(str(tape.get(i, 0)) for i in range(min(left_ones), h))
                    r_str = "".join(str(tape.get(i, 0)) for i in range(h+1, max(ones)+1))
                    w_r = r_str[::-1]
                    if w_r.startswith("100") and w_r.endswith("1"):
                        parts = w_r[3:-1].split("00")
                        if all(len(p)%2==0 and not (set(p)-{'1'}) for p in parts):
                            vals = [len(p)//2 for p in parts]
                            outcome = f"PREFIX KP(L={l_str}; ds={vals[:-2]}; a={vals[-2]}; b={vals[-1]}) @{step}"
                            break
        print(f"  k={k:2d}: {outcome}")
