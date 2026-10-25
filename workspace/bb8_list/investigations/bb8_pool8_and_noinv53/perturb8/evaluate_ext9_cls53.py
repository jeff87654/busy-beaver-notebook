import collections, json, re, sys

BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, BASE)
from analyze_ext9 import load_tsv
from classify_all_mut8_exact import parents, kl, run_from_k, parse_k
from check_blank_first_k import get_blank_k_seq

rows = load_tsv('scan_ext9_cls53.tsv')
print(f"Loaded {len(rows)} rows from scan_ext9_cls53.tsv")

# 1. Inspect all NON_MOD2_E! and KHKHKHKH (a_acc) machines in detail
print("\n================ 1. NON_MOD2_E! & REVERSED-E IN ext9_cls53 ================")
seen = set()
for r in rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if tm in seen:
        continue
    if cat == 'NON_MOD2_E!' or (epat == 'KHKHKHKH' and cat != 'B_ACC_OPEN'):
        seen.add(tm)
        p = parents[pid]
        t = kl.tmpl(tm, p['tmpl_str'])
        B0 = p['B0']
        print(f"\n* [{cat}] ({epat}) {pid} {grp} {mut} | {tm}")
        print(f"  binfo={binfo} | btrace={btrace}")
        print(f"  det={det}")
        e_res = []
        for a in range(1, 21):
            er = run_from_k(tm, t, [], a, B0, req_B0=B0)
            if er[0] == 'K':
                e_res.append(f"{a}:K(L={len(er[1][0])},d1={er[1][0][0] if er[1][0] else '-'},a={er[1][1]})")
            else:
                e_res.append(f"{a}:{er[0]}")
        print(f"  E(1..20): {'  '.join(e_res)}")

# 2. Classify all unique B_HITS_HPAR and B_DEP_A_PAR! machines in scan_ext9_cls53.tsv
print("\n================ 2. B_HITS_HPAR & B_DEP_A_PAR! STRUCTURAL CLASSES ================")
seen_tm = set()
by_b_struct = collections.defaultdict(list)

def parse_bk_det(b_str):
    if '/' in b_str:
        p0, p1 = b_str.split('/', 1)
    else:
        p0, p1 = b_str, b_str
    def parse_one(p):
        m = re.match(r'^\[([^\]]*)\];(-?\d+);(-?\d+)$', p)
        if not m:
            return None
        L = []
        for x in m.group(1).split(','):
            x = x.strip()
            if not x:
                continue
            if '^' in x:
                val, cnt = x.split('^')
                L.extend([int(val)] * int(cnt))
            else:
                L.append(int(x))
        a = int(m.group(2))
        b = int(m.group(3))
        return (L[1:], a, b)
    r0 = parse_one(p0)
    r1 = parse_one(p1)
    if not (r0 and r1):
        return None
    return (r0, r1)

for r in rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if tm in seen_tm or cat not in ('B_HITS_HPAR', 'B_DEP_A_PAR!'):
        continue
    seen_tm.add(tm)
    left_part = det.split(' | ')[0]
    tokens = {kv.split('=', 1)[0]: kv.split('=', 1)[1] for kv in left_part.split(' ') if '=' in kv}
    b1 = parse_bk_det(tokens.get('B1', ''))
    b2 = parse_bk_det(tokens.get('B2', ''))
    b3 = parse_bk_det(tokens.get('B3', ''))
    if not (b1 and b2 and b3):
        continue
    l1, p1_0, p1_1 = len(b1[0][0]), b1[0][1] % 2, b1[1][1] % 2
    l2, p2_0, p2_1 = len(b2[0][0]), b2[0][1] % 2, b2[1][1] % 2
    l3, p3_0, p3_1 = len(b3[0][0]), b3[0][1] % 2, b3[1][1] % 2
    if l1 > 1:
        sig = f"RUNAWAY_B1 (l1={l1})"
    else:
        sig = f"{epat} | B1(l={l1},p={p1_0}/{p1_1}) B2(l={l2},p={p2_0}/{p2_1},t={b2[0][0][1:]}) B3(l={l3},p={p3_0}/{p3_1},t={b3[0][0][1:]})"
    by_b_struct[sig].append(r)

print(f"Unique B_HITS_HPAR / B_DEP_A_PAR! machines in ext9_cls53: {len(seen_tm)}")
for sig, items in sorted(by_b_struct.items()):
    best = max(items, key=lambda x: (int(re.search(r'nE=(\d+)', x[6]).group(1)), int(re.search(r'maxL=(\d+)', x[6]).group(1))))
    print(f"  {len(items):4d}x : {sig}")
    print(f"         best: {best[0]} {best[2]} {best[6]} {best[7]} | {best[3]}")
