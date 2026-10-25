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

base_11 = [
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RD0RI_0LG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LE0RI_0LG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RI0RI_0LG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RD0RI_1LH---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB1RI_0LD---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RD1RI_0LD---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LE1RI_0LD---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB1RI_1RG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RD1RI_1RG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LE1RI_1RG---",
]

# Note: for champ_232 (G0=1LC), exhaustion K(0^k; a; 0) hits C1 on the exact same tape!
for idx, tm231 in enumerate(base_11):
    tm232 = tm231.replace("_0LD0RB_", "_1LC0RB_")
    tr = parse_tm9(tm232)
    res_map = {}
    for k in [2, 3, 4, 5, 20]:
        N = 6
        left_str = "10"*(2*k-1) + "11001"
        right_str = "100" + "1100"*N + "1"
        full_str = left_str + "1" + right_str
        h0 = len(left_str)
        tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
        h, s = h0, 2
        out = "T"
        for step in range(1, 80001):
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
                if res is not None and res[0] == "K" and len(res[2]) >= N:
                    ds, a = res[2], res[3]
                    exp_ds = [1]*(N-1) + [0] + [3]*(k//2 - 1) + [4, 0, 0]
                    out = f"K(L={len(ds)},match={ds==exp_ds and a==0})@{step}"
                    break
        res_map[k] = out
    print(f"[{idx+1:2d}] {tm232} | " + " ".join(f"k{k}={res_map[k]}" for k in [2, 3, 4, 5, 20]))
