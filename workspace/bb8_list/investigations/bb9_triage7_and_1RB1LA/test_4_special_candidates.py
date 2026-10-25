import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

def parse_tm9(tm_str):
    rows = tm_str.split("_")
    return [t for row in rows for t in (row[:3], row[3:])]

def fmt_tape(tape, h, s):
    ones = [i for i, v in tape.items() if v == 1]
    mn = min(ones + [h])
    mx = max(ones + [h])
    left = "".join(str(tape.get(i, 0)) for i in range(mn, h))
    right = "".join(str(tape.get(i, 0)) for i in range(h+1, mx+1))
    return f"{left}[{chr(65+s)}{tape.get(h,0)}]{right}"

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

cands = [
    ("TKTKTTTTT_H0", "1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_0LC1LG"),
    ("KKTKKKKTK_I0", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RA1LI_---1LD"),
    ("TKTKTKTKT_I1", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LG1LI_1LC---"),
    ("KTKKKTKKK_I1", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RI0LD_1RF---"),
    ("MIXED_k20_K", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_0RA1LB"),
]

for label, tm in cands:
    print(f"\n=== {label}: {tm} ===")
    tr = parse_tm9(tm)
    for k in [1, 2, 3, 4, 5, 6, 20]:
        N = 25 if k == 20 else 6
        left_str = "10"*(2*k-1) + "11001"
        right_str = "100" + "1100"*N + "1"
        full_str = left_str + "1" + right_str
        h0 = len(left_str)
        tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
        h, s = h0, 2
        out = "T"
        first_e0_left = None
        for step in range(1, 60001):
            b = tape.get(h, 0)
            act = tr[2*s + b]
            if act == "---":
                out = f"HALT({chr(65+s)}{b})@{step}"
                break
            if int(act[0]): tape[h] = 1
            else: tape.pop(h, None)
            h += 1 if act[1] == "R" else -1
            s = ord(act[2]) - 65
            ones = [i for i, v in tape.items() if v == 1]
            if s == 4 and tape.get(h, 0) == 0:
                res = parse_K_or_KP(tape, h, s)
                if res is not None and res[0] == "K" and len(res[2]) >= N - 2:
                    out = f"CLEAN_K(L={len(res[2])} [N+{len(res[2])-N}], tail={res[2][N-1:]}; a={res[3]})@{step}"
                    break
                if h == min(ones) - 1 and first_e0_left is None:
                    first_e0_left = f"step {step}: {fmt_tape(tape, h, s)[:60]}"
        print(f"  k={k:2d} (N={N:2d}): {out}")
        if out == "T" and first_e0_left:
            print(f"               first_left_E0 = {first_e0_left}")
