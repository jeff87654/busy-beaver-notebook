import os, sys, json, ctypes
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040)
except Exception:
    pass

sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import bcfg, kl
from build_and_profile_parents import run_from_k, parse_k

with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8\parents_profile.json') as f:
    parents = json.load(f)

# Let's check why cls53_03_d had C1, D1, H0 in start_only!
for pid in ['cls53_03_d', 'cls53_04_d', 'cls53_05_d', 'cls53_17_n', 'cls53_36_p', 'cls53_38_p', 'cls53_43_p',
            'pool8_01', 'pool8_02', 'pool8_06', 'pool8_07', 'pool8_09', 'pool8_12', 'pool8_13', 'pool8_18']:
    p = next(x for x in parents if x['id'] == pid)
    M = p['machine']
    t = kl.tmpl(M, p['tmpl_str'])
    B0 = p['B0']
    print(f"=== {pid} ({p['group']}) : {M} | tmpl={p['tmpl_str']} B0={B0} ===")
    if p['mode'] == 'a_acc':
        tests = [
            ('D_even', [3], 4, B0),
            ('D_odd',  [3], 5, B0),
            ('B1_e',   [2, 0], 4, B0),
            ('B1_o',   [2, 0], 5, B0),
            ('B2_e',   [2, 0, 0], 6, B0),
            ('B2_o',   [2, 0, 0], 7, B0),
            ('B3_e',   [2, 0, 0, 0], 8, B0),
            ('B3_o',   [2, 0, 0, 0], 9, B0),
            ('E_6',    [], 6, B0),
            ('E_7',    [], 7, B0),
            ('E_8',    [], 8, B0),
            ('E_9',    [], 9, B0),
        ]
    else:
        nE = p['nE']
        tests = [
            ('D_a2',   [3], 2, 10),
            ('R2_b10', [3], 0, 10),
            ('R2_b11', [3], 0, 11),
            ('B1_b10', [2, 0], 0, 10),
            ('B1_b11', [2, 0], 0, 11),
            ('B2_b10', [2, 0, 0], 0, 10),
            ('B2_b11', [2, 0, 0], 0, 11),
            ('B3_b10', [2, 0, 0, 0], 0, 10),
            ('E_b14',  [0]*nE, 0, 14),
            ('E_b15',  [0]*nE, 0, 15),
            ('E_b16',  [0]*nE, 0, 16),
            ('E_b17',  [0]*nE, 0, 17),
        ]
    req_B0 = B0 if p['mode'] == 'a_acc' else None
    for name, ds, a, b in tests:
        knd, r, u, st = run_from_k(M, t, ds, a, b, 50000, req_B0=req_B0)
        r_str = f"K(len={len(r[0])},a={r[1]},b={r[2]})" if knd == 'K' else str(r)
        print(f"  {name:8s}: {knd} {r_str:24s} ({st:5d} st) | used={','.join(sorted(u))}")
