import collections, json, re, sys

BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, BASE)
from evaluate_ext9_cls53 import rows, parents, kl, run_from_k, parse_k, parse_bk_det
from check_blank_first_k import get_blank_k_seq

# 1. Analyze the 6 Period-7 (KKKKKKKH) machines in detail!
print("================ 1. PERIOD-7 EXHAUSTION GATE (KKKKKKKH) ================")
seen = set()
for r in rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if epat == 'KKKKKKKH' and tm not in seen:
        seen.add(tm)
        p = parents[pid]
        t = kl.tmpl(tm, p['tmpl_str'])
        B0 = p['B0']
        print(f"\nMachine: {pid} {mut} | {tm}")
        for k in range(1, 7):
            rk5 = run_from_k(tm, t, [2] + [0]*k, 5, B0, req_B0=B0)
            rk6 = run_from_k(tm, t, [2] + [0]*k, 6, B0, req_B0=B0)
            lbk5 = run_from_k(tm, t, [1] + [0]*k, 5, B0, req_B0=B0)
            print(f"  B{k}(a=5): {rk5[1] if rk5[0]=='K' else rk5} | B{k}(a=6): {rk6[1] if rk6[0]=='K' else rk6} | LEFT_B{k}(a=5): {lbk5[1] if lbk5[0]=='K' else lbk5}")
        for a in range(1, 29):
            er = run_from_k(tm, t, [], a, B0, req_B0=B0)
            if er[0] == 'K':
                ds, ao, bo = er[1]
                print(f"  E({a:2d}) [a%14={a%14:2d}, a%7={a%7}]: K len={len(ds):2d} a_out={ao:2d} ds={ds}")
            else:
                print(f"  E({a:2d}) [a%14={a%14:2d}, a%7={a%7}]: HALT at {er[1]} ({er[2]} steps)")
        break # All 6 have identical det; let's check if all 6 have identical rules

# 2. Analyze the 2 Mod-4 Exhaustion Gate (HKKKHKKK) machines in detail!
print("\n================ 2. MOD-4 EXHAUSTION GATE (HKKKHKKK) ================")
for r in rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if epat == 'HKKKHKKK' and tm not in seen:
        seen.add(tm)
        p = parents[pid]
        t = kl.tmpl(tm, p['tmpl_str'])
        B0 = p['B0']
        print(f"\nMachine: {pid} {mut} | {tm}")
        for k in range(1, 6):
            rk5 = run_from_k(tm, t, [2] + [0]*k, 5, B0, req_B0=B0)
            rk6 = run_from_k(tm, t, [2] + [0]*k, 6, B0, req_B0=B0)
            print(f"  B{k}(a=5): {rk5[1] if rk5[0]=='K' else rk5} | B{k}(a=6): {rk6[1] if rk6[0]=='K' else rk6}")
        for a in range(1, 17):
            er = run_from_k(tm, t, [], a, B0, req_B0=B0)
            if er[0] == 'K':
                ds, ao, bo = er[1]
                print(f"  E({a:2d}) [a%4={a%4}]: K len={len(ds):2d} a_out={ao:2d} ds={ds}")
            else:
                print(f"  E({a:2d}) [a%4={a%4}]: HALT at {er[1]} ({er[2]} steps)")

# 3. Analyze the 4 Reversed-Parity Gate (KHKHKHKH) machines on G_HALT_E2!
print("\n================ 3. REVERSED-PARITY GATE (KHKHKHKH on G_HALT_E2) ================")
for r in rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if epat == 'KHKHKHKH' and cat != 'B_ACC_OPEN' and tm not in seen:
        seen.add(tm)
        p = parents[pid]
        t = kl.tmpl(tm, p['tmpl_str'])
        B0 = p['B0']
        ks = get_blank_k_seq(tm, t, maxs=50000, req_B0=B0)
        print(f"\nMachine: {pid} {mut} | {tm}")
        print(f"  startup K-seq: {ks}")
        for k in range(1, 6):
            rk5 = run_from_k(tm, t, [2] + [0]*k, 5, B0, req_B0=B0)
            rk6 = run_from_k(tm, t, [2] + [0]*k, 6, B0, req_B0=B0)
            print(f"  B{k}(a=5): {rk5[1] if rk5[0]=='K' else rk5} | B{k}(a=6): {rk6[1] if rk6[0]=='K' else rk6}")
        for a in range(1, 13):
            er = run_from_k(tm, t, [], a, B0, req_B0=B0)
            if er[0] == 'K':
                ds, ao, bo = er[1]
                print(f"  E({a:2d}): K len={len(ds):2d} a_out={ao:2d} ds={ds}")
            else:
                print(f"  E({a:2d}): HALT at {er[1]}")

# 4. Analyze the 39 B1(l=1,p=0/0) B2(l=1,p=1/1) machines!
print("\n================ 4. B1(l=1,p=0/0) B2(l=1,p=1/1) MACHINES ================")
for r in rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if tm in seen or cat not in ('B_HITS_HPAR', 'B_DEP_A_PAR!'):
        continue
    left_part = det.split(' | ')[0]
    tokens = {kv.split('=', 1)[0]: kv.split('=', 1)[1] for kv in left_part.split(' ') if '=' in kv}
    b1 = parse_bk_det(tokens.get('B1', ''))
    b2 = parse_bk_det(tokens.get('B2', ''))
    if b1 and b2 and len(b1[0][0]) == 1 and b1[0][1]%2 == 0 and len(b2[0][0]) == 1 and b2[0][1]%2 == 1:
        seen.add(tm)
        p = parents[pid]
        t = kl.tmpl(tm, p['tmpl_str'])
        B0 = p['B0']
        e1 = run_from_k(tm, t, [], 1, B0, req_B0=B0)
        e3 = run_from_k(tm, t, [], 3, B0, req_B0=B0)
        e5 = run_from_k(tm, t, [], 5, B0, req_B0=B0)
        e7 = run_from_k(tm, t, [], 7, B0, req_B0=B0)
        print(f"  {pid} {mut} ({btrace}) | {tm}")
        print(f"    det={det[:100]}")
        for a, er in [(1, e1), (3, e3), (5, e5), (7, e7)]:
            if er[0] == 'K':
                print(f"    E({a}): len={len(er[1][0])} ds={er[1][0]} a_out={er[1][1]}")
