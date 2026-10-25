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

reps = [
    ("KKTKKTKKT", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1RI0RG"),
    ("KKTKKKKTK", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1RI1RB"),
    ("KTKKKTKKK", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0LI1RG_1LC---"),
    ("TKTKTTTKT", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LI0LG_1LB---"),
    ("TKTKTTTTT", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LI0LH_1LB---"),
    ("TKTTKTTTK", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RI0LG_---0RC"),
    ("TKKKKKKKK", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0LC0RI_1LA---"),
    ("KKTKKK_113", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB1RG_------"),
]

for label, tm in reps:
    print(f"\n=== {label}: {tm} ===")
    tr = parse_tm9(tm)
    for k in range(1, 7):
        N = 6
        left_str = "10"*(2*k-1) + "11001"
        right_str = "100" + "1100"*N + "1"
        full_str = left_str + "1" + right_str
        h0 = len(left_str)
        tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
        h, s = h0, 2
        kps = []
        out = "T"
        for step in range(1, 30001):
            b = tape.get(h, 0)
            act = tr[2*s + b]
            if act == "---":
                out = f"H({chr(65+s)}{b})@{step}"
                break
            if int(act[0]): tape[h] = 1
            else: tape.pop(h, None)
            h += 1 if act[1] == "R" else -1
            s = ord(act[2]) - 65
            if s == 4 and tape.get(h, 0) == 0:
                res = parse_K_or_KP(tape, h, s)
                if res is not None:
                    kind, l_str, ds, a, b_val = res
                    if kind == "K" and len(ds) >= N - 3:
                        out = f"K(L={len(ds)}, ds=..{ds[-4:]}; a={a}; b={b_val})@{step}"
                        break
                    elif kind == "KP":
                        if not kps or kps[-1][0] != l_str:
                            kps.append((l_str, f"KP(L={l_str}; len={len(ds)}, ds=..{ds[-4:]}; a={a}; b={b_val})@{step}"))
        print(f"  k={k}: {out}")
        for _, kp_str in kps:
            print(f"       {kp_str}")
