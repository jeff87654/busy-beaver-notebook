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
from check_extra_top_machines import parse_k, get_blank_k_seq

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

p = parents['cls53_38_p']
B0 = p['B0']

specials = [
    ("B1(l=0,p=0/1) E411", "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1RH0RF_---0RC_1LH1LG_1LD0RI_0LE1RH"),
    ("B1(l=1,p=1/1) B2(l=1,p=0/0) E35->30", "1RB1LA_1LC1RE_1RD1RC_0LA0LG_0RG0RF_---0RC_1LH1LG_1LD1LI_1RE0LI"),
    ("B1(l=1,p=1/1) B2(l=1,p=0/0) E161", "1RB1LA_1LC1RE_1RD1RC_0LA0LG_0RG0RF_---0RC_1LH1LG_1LD1RI_1LB1LI"),
    ("B1(l=1,p=0/0) E131->330", "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1RI0RF_---0RC_1LH1LG_1LD1LD_0RG---"),
    ("B1(l=1,p=1/1) B2(l=2,p=0/0) E536", "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LH0RF_---0RC_1LH1LG_1LD1LI_1RE0LI"),
]

for label, tm in specials:
    t = kl.tmpl(tm, p['tmpl_str'])
    print(f"\n=== {label} | {tm} ===")
    bseq = get_blank_k_seq(tm, t, req_B0=B0)
    for st, k in bseq[:5]:
        print(f"  blank st={st}: {k}")
    for a in (5, 7, 9, 11):
        er = run_from_k(tm, t, [], a, B0, req_B0=B0)
        if er[0] == 'K':
            ds, ao, bo = er[1]
            print(f"  E({a:2d}): len={len(ds)} d1..3={ds[:3]} sfx={ds[-2:]} a_out={ao}")
        else:
            print(f"  E({a:2d}): {er}")
