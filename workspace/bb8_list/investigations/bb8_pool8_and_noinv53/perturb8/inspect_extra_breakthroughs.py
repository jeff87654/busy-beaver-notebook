import os, json, re, collections, sys, ctypes

try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040)
except Exception:
    pass

BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import bcfg, kl

parents = {p['id']: p for p in json.load(open(BASE + r'\parents_profile.json'))}

from test_period16_variants import parse_k, get_used_in_k, trace_blank

def run_from_k(M, t, ds, a, b, maxs=100000, req_B0=None):
    mir = t['o'] == 'L'
    tr = {}
    for q, row in enumerate(M.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-':
                d = 1 if x[1] == 'R' else -1
                tr[(q, c)] = (int(x[0]), -d if mir else d, ord(x[2]) - 65)
    w = kl.word(t, ds, a, b)
    tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
    pos = len(w)
    Q = ord(t['q']) - 65
    q = Q
    for st in range(maxs):
        c = tape.get(pos, 0)
        if st > 0 and c == 0 and q == Q:
            ones = [i for i, v in tape.items() if v]
            if ones and pos > max(ones):
                lo = min(ones)
                ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
                k = parse_k(ww, t, req_B0=req_B0)
                if k is not None:
                    return ('K', k, st)
        if (q, c) not in tr:
            return ('H', chr(65+q) + str(c), st)
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return ('T', None, maxs)

# 1. Test p2slot_p_13 HKKKHKKK machine:
tm1 = "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LH0RF_1LF0RC_1LH1LG_1LD0LI_---1LE"
p1 = parents['cls53_38_p']
t1 = kl.tmpl(tm1, p1['tmpl_str'])
B0_1 = p1['B0']

print("=== 1. p2slot_p_13 HKKKHKKK (Mod-4 Gate with EVEN B1!) ===")
print("TM:", tm1)
for k in range(1, 5):
    rb = run_from_k(tm1, t1, [2]+[0]*k, 6, B0_1, req_B0=B0_1)
    lb = run_from_k(tm1, t1, [1]+[0]*k, 6, B0_1, req_B0=B0_1)
    print(f"  B{k}(a=6): {rb[:2]} | LEFT_B{k}(a=6): {lb[:2]}")
for a in range(1, 21):
    re_a = run_from_k(tm1, t1, [], a, B0_1, req_B0=B0_1)
    if re_a[0] == 'K':
        ds, ao, bo = re_a[1]
        print(f"  E({a:2d}) [a%4={a%4}]: K len={len(ds):2d} d1..3={ds[:3]} sfx={ds[-2:]} a_out={ao} (a_out%4={ao%4})")
    else:
        print(f"  E({a:2d}) [a%4={a%4}]: {re_a}")

# 2. Test cand162_t_F01L_50 KHHHKHHH machine:
tm2 = "1RB1RE_1RC1RB_0LD0LG_0RA1LD_---1RF_1LH0RB_1LC1LG_0LI0LH_0RG0LI"
p2 = parents['cand162_t_F01L_50']
t2 = kl.tmpl(tm2, p2['tmpl_str'])
B0_2 = p2['B0']
print("\n=== 2. cand162_t_F01L_50 KHHHKHHH (Mod-4 Gate where ONLY 2 mod 4 survives!) ===")
print("TM:", tm2)
for k in range(1, 5):
    rb = run_from_k(tm2, t2, [2]+[0]*k, 6, B0_2, req_B0=B0_2)
    lb = run_from_k(tm2, t2, [1]+[0]*k, 6, B0_2, req_B0=B0_2)
    print(f"  B{k}(a=6): {rb[:2]} | LEFT_B{k}(a=6): {lb[:2]}")
for a in range(1, 17):
    re_a = run_from_k(tm2, t2, [], a, B0_2, req_B0=B0_2)
    if re_a[0] == 'K':
        ds, ao, bo = re_a[1]
        print(f"  E({a:2d}) [a%4={a%4}]: K len={len(ds):2d} d1..3={ds[:3]} sfx={ds[-2:]} a_out={ao} (a_out%4={ao%4})")
    else:
        print(f"  E({a:2d}) [a%4={a%4}]: {re_a}")

# 3. Test p2slot_p_16 KHTKHTKH machine:
tm3 = "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1RG0RF_1LF0RC_1LH1LG_1LD0LI_---0LA"
print("\n=== 3. p2slot_p_16 KHTKHTKH (Mod-3 Gate on p!) ===")
print("TM:", tm3)
for k in range(1, 5):
    rb = run_from_k(tm3, t1, [2]+[0]*k, 6, B0_1, req_B0=B0_1)
    lb = run_from_k(tm3, t1, [1]+[0]*k, 6, B0_1, req_B0=B0_1)
    print(f"  B{k}(a=6): {rb[:2]} | LEFT_B{k}(a=6): {lb[:2]}")
for a in range(1, 17):
    re_a = run_from_k(tm3, t1, [], a, B0_1, req_B0=B0_1, maxs=20000)
    if re_a[0] == 'K':
        ds, ao, bo = re_a[1]
        print(f"  E({a:2d}) [a%3={a%3}]: K len={len(ds):2d} d1..3={ds[:3]} sfx={ds[-2:]} a_out={ao} (a_out%3={ao%3})")
    else:
        print(f"  E({a:2d}) [a%3={a%3}]: {re_a}")
