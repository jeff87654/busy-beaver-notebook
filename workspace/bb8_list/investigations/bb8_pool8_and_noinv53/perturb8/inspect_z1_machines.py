import sys
BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, BASE)
from classify_all_mut8_exact import parents, kl, run_from_k

cases = [
    ("cls53_36_p", "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LD0RF_---0RH_1LE1LG_0RI1RC_1LA0RD"),
    ("cls53_36_p", "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LD0RF_---0RH_1LE1LG_0RI1RC_1LA0LE"),
    ("cls53_03_d", "1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LB0RG_1LE1LF_---0RH_0RI1RA_0LC1RG"),
    ("cls53_03_d", "1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LB0RG_1LE1LF_---0RH_1RI1RA_1LB1LG"),
]

for pid, tm in cases:
    p = parents[pid]
    t = kl.tmpl(tm, p['tmpl_str'])
    B0 = p['B0']
    print(f"\n=== {pid} | {tm} ===")
    for k in range(1, 5):
        r5 = run_from_k(tm, t, [2]+[0]*k, 5, B0, req_B0=B0)
        lb5 = run_from_k(tm, t, [1]+[0]*k, 5, B0, req_B0=B0)
        print(f"  B{k}(5): {r5[1] if r5[0]=='K' else r5} | LEFT_B{k}(5): {lb5[1] if lb5[0]=='K' else lb5}")
    for a in (1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21):
        er = run_from_k(tm, t, [], a, B0, req_B0=B0)
        if er[0] == 'K':
            print(f"  E({a:2d}): len={len(er[1][0]):2d} a_out={er[1][1]:2d} ds={er[1][0]}")
        else:
            print(f"  E({a:2d}): {er}")
