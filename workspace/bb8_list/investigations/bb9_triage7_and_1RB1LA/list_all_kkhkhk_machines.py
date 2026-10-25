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

tsv = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_triage7_and_1RB1LA\enum_champ231_9.tsv'
with open(tsv) as f:
    lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]

kkhkhk_list = []
for l in lines:
    parts = l.split('\t')
    tag, tm, info = parts[0], parts[1], parts[2]
    if 'k20=K(L37,a0,d0,0)' in info:
        tr = parse_tm9(tm)
        # Check k=3 (N=6) for HALT within 70,000 steps
        N = 6
        k = 3
        left_str = "10"*(2*k-1) + "11001"
        right_str = "100" + "1100"*N + "1"
        full_str = left_str + "1" + right_str
        h0 = len(left_str)
        tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
        h, s = h0, 2
        for step in range(1, 70001):
            b = tape.get(h, 0)
            act = tr[2*s + b]
            if act == "---":
                kkhkhk_list.append((tm, f"H({chr(65+s)}{b})@{step}", info.split('|')[1].strip()))
                break
            if int(act[0]): tape[h] = 1
            else: tape.pop(h, None)
            h += 1 if act[1] == "R" else -1
            s = ord(act[2]) - 65

print(f"Total KKHKHK 3-round f_{{omega+1}} halters in enum_champ231_9.tsv: {len(kkhkhk_list)}")
for idx, (tm, h_info, k20_info) in enumerate(kkhkhk_list):
    print(f"  [{idx+1:2d}] {tm} | k3={h_info} | {k20_info}")
