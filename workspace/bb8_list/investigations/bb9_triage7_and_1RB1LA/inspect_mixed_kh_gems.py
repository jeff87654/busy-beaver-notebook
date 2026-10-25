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

def test_machine(label, tm_str, k_list=range(1, 10), N=6, max_steps=150000):
    print(f"\n=== {label}: {tm_str} ===")
    tr = parse_tm9(tm_str)
    for k in k_list:
        left_str = "10"*(2*k-1) + "11001"
        right_str = "100" + "1100"*N + "1"
        full_str = left_str + "1" + right_str
        h0 = len(left_str)
        tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
        h, s = h0, 2
        first_kp = None
        final_res = "T"
        for step in range(1, max_steps + 1):
            b = tape.get(h, 0)
            act = tr[2*s + b]
            if act == "---":
                final_res = f"HALT({chr(65+s)}{b})@{step}"
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
                        final_res = f"CLEAN_K(len={len(ds)}, ds=..{ds[-4:]}; a={a})@{step}"
                        break
                    elif kind == "KP" and first_kp is None and len(ds) >= N - 3:
                        first_kp = f"KP(L={l_str}; len={len(ds)}, ds=..{ds[-3:]}; a={a})@{step}"
        print(f"  k={k:2d}: {final_res:52s} | first_kp={first_kp}")

test_machine("KHTKHTKHT", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LC0RI_1LC---", range(1, 10))
test_machine("HHKHHKHHK", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RA0RI_0LG---", range(1, 10))
test_machine("HKTTTTTTT", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LD1RI_0RH---", range(1, 8))
test_machine("HKKTTTTTT", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LH0LI_1LD---", range(1, 8))
test_machine("HTKTTTTTT", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1RF1LC", range(1, 8))
test_machine("THKTTTTTT", "1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1LI_1RB0LC", range(1, 8))
test_machine("KKKKKKKKK_H20", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LG0RI_0RB---", [1, 2, 3, 4, 20])
