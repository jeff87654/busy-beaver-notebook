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

cands = []
seen = set()
for l in lines:
    parts = l.split('\t')
    tag, tm, info = parts[0], parts[1], parts[2]
    if tag == 'CLEAN_K' and 'k20=T' in info:
        rows = tm.split('_')
        key = (info, rows[2], rows[7], '---' in rows[8])
        if key not in seen:
            seen.add(key)
            cands.append((tm, info))

print(f"Total CLEAN_K rows with k20=T: {sum(1 for l in lines if 'CLEAN_K' in l and 'k20=T' in l)}, unique keys: {len(cands)}")
# Test k=20 up to 120,000 steps on all unique keys!
hits_k20 = []
for idx, (tm, info) in enumerate(cands):
    tr = parse_tm9(tm)
    k, N = 20, 25
    left_str = "10"*(2*k-1) + "11001"
    right_str = "100" + "1100"*N + "1"
    full_str = left_str + "1" + right_str
    h0 = len(left_str)
    tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
    h, s = h0, 2
    out = "T"
    for step in range(1, 120001):
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
            if res is not None and res[0] == "K" and len(res[2]) >= N - 2:
                out = f"K(L={len(res[2])},a={res[3]})@{step}"
                break
    if out != "T":
        print(f"  [{idx:3d}] {tm} -> k20={out} | {info}")
        if out.startswith("K("):
            hits_k20.append((tm, out, info))

print(f"Found {len(hits_k20)} CLEAN_K (k20=T at 30k) that reach K at k=20 within 120k steps!")
