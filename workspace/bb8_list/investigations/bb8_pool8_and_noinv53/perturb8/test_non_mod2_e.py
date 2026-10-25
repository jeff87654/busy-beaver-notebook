import json, sys
BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, BASE)
from check_exact_multiround_rules import load_tsv, parents, kl, run_from_k

cand_rows = load_tsv('scan_mut8_cand162.tsv')
seen = set()
for r in cand_rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if cat == 'NON_MOD2_E!' and tm not in seen:
        seen.add(tm)
        p = parents[pid]
        t = kl.tmpl(tm, p['tmpl_str'])
        B0 = p['B0']
        print(f"\n=== {pid} {mut} | {tm} | {btrace} ===")
        for a in range(1, 15):
            res = run_from_k(tm, t, [], a, B0, req_B0=B0)
            if res[0] == 'K':
                ds, a_out, b_out = res[1]
                s_mod2 = (a_out + sum(ds)) % 2
                print(f"  E({a:2d}) [a%6={a%6}]: K len={len(ds):2d} a_out={a_out} sum(ds)={sum(ds)} (a_out+sum)%2={s_mod2} ds={ds}")
            else:
                print(f"  E({a:2d}) [a%6={a%6}]: {res[0]} at {res[1]} ({res[2]} steps)")
        # Also test direct simulation from small ds=[1, 1], a=3 and ds=[2, 1], a=3 to verify theorem!
        for test_ds, test_a in [([1], 3), ([2], 3), ([1, 1], 3), ([2, 1], 3)]:
            # simulate step by step through K-configs until E ([], a_final)
            cur_ds, cur_a = list(test_ds), test_a
            while any(x > 0 for x in cur_ds):
                res = run_from_k(tm, t, cur_ds, cur_a, B0, req_B0=B0)
                assert res[0] == 'K', f"Unexpected {res}"
                cur_ds, cur_a, _ = res[1]
            e_res = run_from_k(tm, t, cur_ds, cur_a, B0, req_B0=B0)
            pred_halt = ((test_a + sum(test_ds)) % 2 == 1)
            print(f"  Test ds={test_ds}, a={test_a}: pred_halt={pred_halt} -> reached E with a_final={cur_a} (a_final%6={cur_a%6}), E_res={e_res[0]}")
