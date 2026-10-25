import os, json, re, collections, sys, ctypes

try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040)
except Exception:
    pass

BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'

def load_tsv(fn):
    path = BASE + '\\' + fn
    raw = open(path, 'rb').read()
    text = raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8', errors='ignore')
    rows = []
    for line in text.splitlines():
        parts = line.rstrip('\r\n').split('\t')
        if len(parts) >= 9:
            rows.append(parts[:9])
    return rows

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
        return (L[1:], a % 2, a)
    r0 = parse_one(p0)
    r1 = parse_one(p1)
    if not r0 or not r1:
        return None
    return (r0, r1)

def classify_row(r):
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if binfo.startswith('H:'):
        m_ne = re.search(r'nE=(\d+)', binfo)
        ne = int(m_ne.group(1)) if m_ne else 1
        return f"HALT_DIRECT_E{ne}"
    if cat == 'LOCKED_A_PAR':
        return "LOOP_F_OMEGA_PLUS_1 (LOCKED_ODD_A)"
    if cat == 'B_ACC_OPEN':
        if ';3;1' in det or ';2;1' in det:
            if btrace == '-' or 'nE=0' in binfo:
                return "HALT_E1_STARTUP (B_ACC_ENGINE_II_H0_MUT)"
            return "HALT_E2 (B_ACC_ENGINE_II_GROUP_B)"
        return "LOOP_F_OMEGA_PLUS_1 (B_ACC_ENGINE_I_MOD2_INV)"
    if epat == 'KKKKKKKH':
        return "LOOP_F_OMEGA_PLUS_1 (PERIOD_16_GATE_0_9_MOD_16_CYCLE)"
    if epat == 'HKKHKKHK':
        return "HALT_E2 (MOD_3_GATE_5A_PLUS_7_EXACT_3_MOD_6)"
    if epat == 'HKKKHKKK':
        m1 = re.search(r'B1=([^\s]+)', det)
        b1 = parse_bk_det(m1.group(1)) if m1 else None
        if b1 and b1[0][1] == 0:
            return "HALT_E2 (MOD_4_GATE_EVEN_B1_HITS_2_MOD_4)"
        return "LOOP_F_OMEGA_PLUS_1 (MOD_4_GATE_ODD_B1_AVOIDS_2_MOD_4)"
    if epat == 'KHHHKHHH':
        return "HALT_E2 (MOD_4_GATE_3A_PLUS_6_HITS_0_MOD_4)"
    if epat == 'KHTKHTKH':
        return "HALT_E1 (MOD_3_GATE_5A_PLUS_6_HITS_1_MOD_3)"
    if epat in ('HHHKHKHK', 'HKHKHHHH', 'HKHKHKHH'):
        return "HALT_E2 (PARTIAL_E_GATE)"
    if epat == 'KHKHKHKH':
        return "LOOP_F_OMEGA_PLUS_1 (REVERSED_E_EVEN_A_INV)"

    m1 = re.search(r'B1=([^\s]+)', det)
    m2 = re.search(r'B2=([^\s]+)', det)
    m3 = re.search(r'B3=([^\s]+)', det)
    b1 = parse_bk_det(m1.group(1)) if m1 else None
    b2 = parse_bk_det(m2.group(1)) if m2 else None
    b3 = parse_bk_det(m3.group(1)) if m3 else None
    if not (b1 and b2 and b3):
        return f"OTHER ({cat})"
    l1 = len(b1[0][0])
    if l1 > 1:
        return f"LOOP_RUNAWAY_B1 (|L1|={l1}, single-round list grower)"
    p1_0, p1_1 = b1[0][1], b1[1][1]
    l2 = len(b2[0][0])
    p2_0, p2_1 = b2[0][1], b2[1][1]
    if l1 == 0:
        return "LOOP_F_OMEGA_PLUS_1 (GROUP_E_B1_EMPTY_D1_GE_3)"
    if p1_0 == 0 and p1_1 == 0:
        if 'E1->1 ' in btrace:
            return "HALT_E3 (GROUP_D_LEFT_B1_EVEN)"
        if btrace == '-':
            return "HALT_E1_OR_E2 (LEFT_B1_EVEN)"
        return "HALT_E2 (LEFT_B1_EVEN)"
    if p1_0 == 1 and p1_1 == 1 and l2 == 1 and p2_0 == 0 and p2_1 == 0:
        if tm.endswith('_1LB1RC') or tm.endswith('_0LC1RC') or ('E35->30' in btrace):
            return "LOOP_F_OMEGA_PLUS_1 (D1_GE_2_SKIPS_LEFT_B2)"
        return "HALT_E2 (GROUP_G_D1_EQ_1_HITS_LEFT_B2_EVEN)"
    return "LOOP_F_OMEGA_PLUS_1 (B1_ODD_AND_LEN_B2_GE_2)"

# 1. Write perturb8_survivors.tsv (all 787 mut8 rows)
mut8_rows = (
    [('cls53', r) for r in load_tsv('scan_mut8_cls53.tsv')] +
    [('cand162', r) for r in load_tsv('scan_mut8_cand162.tsv')] +
    [('pool8', r) for r in load_tsv('scan_mut8_pool8.tsv')]
)

mut8_verdict_counts = collections.Counter()
with open(BASE + r'\perturb8_survivors.tsv', 'w', encoding='utf-8') as f:
    f.write("source\tparent_id\tparent_group\tmutation\ttm\te_pattern\tcategory\tblank_info\tblank_trace\texact_verdict\tdetails\n")
    for src, r in mut8_rows:
        v = classify_row(r)
        mut8_verdict_counts[v] += 1
        f.write("\t".join([src] + r[:8] + [v, r[8]]) + "\n")

print(f"Wrote {len(mut8_rows)} rows to perturb8_survivors.tsv")
for v, cnt in sorted(mut8_verdict_counts.items()):
    print(f"  {cnt:5d}x : {v}")

# 2. Write ext9_survivors.tsv (all unique TMs in scan_ext9_cls53, scan_ext9_cand162, scan_ext9_extra)
ext9_all = (
    [('cls53', r) for r in load_tsv('scan_ext9_cls53.tsv')] +
    [('cand162', r) for r in load_tsv('scan_ext9_cand162.tsv')] +
    [('extra', r) for r in load_tsv('scan_ext9_extra.tsv')]
)

seen_ext9 = set()
ext9_out = []
ext9_verdict_counts = collections.Counter()
for src, r in ext9_all:
    tm = r[3]
    if tm in seen_ext9:
        continue
    seen_ext9.add(tm)
    v = classify_row(r)
    ext9_verdict_counts[v] += 1
    ext9_out.append((src, r, v))

with open(BASE + r'\ext9_survivors.tsv', 'w', encoding='utf-8') as f:
    f.write("source\tparent_id\tparent_group\tmutation\ttm\te_pattern\tcategory\tblank_info\tblank_trace\texact_verdict\tdetails\n")
    for src, r, v in ext9_out:
        f.write("\t".join([src] + r[:8] + [v, r[8]]) + "\n")

print(f"\nWrote {len(ext9_out)} unique TMs (from {len(ext9_all)} total rows) to ext9_survivors.tsv")
for v, cnt in sorted(ext9_verdict_counts.items()):
    print(f"  {cnt:5d}x : {v}")
