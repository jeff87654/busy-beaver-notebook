import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

def parse_tm9(tm_str):
    rows = tm_str.split("_")
    return [t for row in rows for t in (row[:3], row[3:])]

def parse_K_or_KP(tape, h, s):
    if s != 4 or tape.get(h, 0) != 0:
        return None
    ones = [i for i, v in tape.items() if v == 1]
    if not ones or h >= max(ones):
        return None
    mn, mx = min(ones), max(ones)
    if h + 4 > mx:
        return None
    if tape.get(h+1, 0) != 1 or tape.get(h+2, 0) != 0 or tape.get(h+3, 0) != 0:
        return None
    r_str = "".join(str(tape.get(i, 0)) for i in range(h+1, mx+1))
    w_r = r_str[::-1]
    if not (w_r.startswith("100") and w_r.endswith("1")):
        return None
    parts = w_r[3:-1].split("00")
    if len(parts) < 2:
        return None
    for p in parts:
        if len(p) % 2 != 0 or (set(p) - {'1'}):
            return None
    vals = [len(p) // 2 for p in parts]
    ds, a, b = vals[:-2], vals[-2], vals[-1]
    if h == mn - 1:
        return ("K", "", ds, a, b)
    else:
        l_str = "".join(str(tape.get(i, 0)) for i in range(mn, h))
        return ("KP", l_str, ds, a, b)

# 1. Verify blank tape start of KKHKHK_144 (both champ_231 G0=0LD and champ_232 G0=1LC variants!)
for name, tm in [
    ("KKHKHK_231_144", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---"),
    ("KKHKHK_231_161", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB1RI_0LD---"),
    ("KKHKHK_232_161", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_0RB1RI_0LD---"),
]:
    tr = parse_tm9(tm)
    tape = {}
    h, s = 0, 0
    for step in range(1, 6000):
        b = tape.get(h, 0)
        act = tr[2*s + b]
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == "R" else -1
        s = ord(act[2]) - 65
        if s == 4 and tape.get(h, 0) == 0:
            res = parse_K_or_KP(tape, h, s)
            if res is not None and res[0] == "K" and len(res[2]) == 20:
                ds, a, b_val = res[2], res[3], res[4]
                print(f"{name}: step {step:4d} -> K(len={len(ds)}, ds={ds}; a={a}; b={b_val}) | I = {(a + sum(ds)) % 2}")
                break

# 2. Verify exact rebuild formula for even k = 2, 4, 6, 8, 10, 20 and halting for odd k = 3, 5, 7, 9, 11, 21
tm = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---"
tr = parse_tm9(tm)
print("\nVerifying exact rebuild / halt on k = 2..11, 20, 21:")
for k in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 20, 21]:
    N = 6
    left_str = "10"*(2*k-1) + "11001"
    right_str = "100" + "1100"*N + "1"
    full_str = left_str + "1" + right_str
    h0 = len(left_str)
    tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
    h, s = h0, 2
    for step in range(1, 80000):
        b = tape.get(h, 0)
        act = tr[2*s + b]
        if act == "---":
            expected_step = 67181 + 82 * (k - 3)
            print(f"  k={k:2d} (odd):  HALT({chr(65+s)}{b}) at step {step} (expected {expected_step}, match={step==expected_step})")
            break
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == "R" else -1
        s = ord(act[2]) - 65
        if s == 4 and tape.get(h, 0) == 0:
            res = parse_K_or_KP(tape, h, s)
            if res is not None and res[0] == "K" and len(res[2]) >= N:
                ds, a = res[2], res[3]
                expected_ds = [1]*(N-1) + [0] + [3]*(k//2 - 1) + [4, 0, 0]
                expected_step = 82 * k + 14
                print(f"  k={k:2d} (even): CLEAN_K at step {step:4d} (exp {expected_step:4d}), len={len(ds)} (exp {N+k//2+2}), exact_ds_match={ds==expected_ds and a==0}")
                break
