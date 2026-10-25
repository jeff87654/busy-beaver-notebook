import collections, json, re, sys

BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, BASE)
from analyze_ext9 import load_tsv
from classify_all_mut8_exact import parents, kl, run_from_k, parse_k
import bcfg

# 1. Summarize scan_ext9_cand162.tsv
rows = load_tsv('scan_ext9_cand162.tsv')
print(f"Total ext9 cand162 survivor rows: {len(rows)}")
pstats = collections.Counter(r[5] for r in rows)
epats = collections.Counter(r[4] for r in rows)
print("pstats:", dict(pstats))
print("epats:", dict(epats))

by_epat = collections.defaultdict(list)
for r in rows:
    by_epat[(r[4], r[1], r[5])].append(r)
for (epat, grp, cat), items in sorted(by_epat.items()):
    best = max(items, key=lambda x: (int(re.search(r'nE=(\d+)', x[6]).group(1)), int(re.search(r'maxL=(\d+)', x[6]).group(1))))
    print(f"  {epat} | {grp:16s} | {cat:13s} | count={len(items):4d} | best: {best[0]} {best[2]} {best[6]} {best[7]} | {best[3]}")

# 2. Build parents_extra_ext9.tsv from:
#    - intact bcfg.BASES for d, e, f, g, n, o, p, q
#    - the 8 HKKHKKHK machines from e and g
#    - the top 2slot_E0_H1 machines from p and q
extra_machines = []
for tag in ('d', 'e', 'f', 'g', 'n', 'o', 'p', 'q'):
    m, tmpl_str, B0, _ = bcfg.BASES[tag]
    extra_machines.append((f"base_{tag}", f"BASE_{tag}", tag, "a_acc", B0, 0, m, tmpl_str))

cand_mut8 = load_tsv('scan_mut8_cand162.tsv')
seen_m = set()
for idx, r in enumerate(cand_mut8):
    if r[5] == 'NON_MOD2_E!' and r[3] not in seen_m:
        seen_m.add(r[3])
        p = parents[r[0]]
        extra_machines.append((f"mod3_{p['tag']}_{len(seen_m)}", f"MOD3_{p['tag']}", p['tag'], "a_acc", p['B0'], 0, r[3], p['tmpl_str']))

cls_mut8 = load_tsv('scan_mut8_cls53.tsv')
for r in cls_mut8:
    if '2slot_E0_H1' in r[2] and r[3] not in seen_m and ('E81->205' in r[7] or 'E91->115' in r[7] or 'E25->65' in r[7] or 'E21->55' in r[7] or 'E17->45' in r[7]):
        seen_m.add(r[3])
        p = parents[r[0]]
        extra_machines.append((f"p2slot_{p['tag']}_{len(seen_m)}", f"P2SLOT_{p['tag']}", p['tag'], "a_acc", p['B0'], 0, r[3], p['tmpl_str']))

# Profile D_used, B_only, E_only, start_only, undef for each extra machine
def rfk_used(M, t, ds, a, b, maxs=50000, req_B0=None):
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
    used = set()
    for st in range(maxs):
        c = tape.get(pos, 0)
        if st > 0 and c == 0 and q == Q:
            ones = [i for i, v in tape.items() if v]
            if ones and pos > max(ones):
                lo = min(ones)
                ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
                k = parse_k(ww, t, req_B0=req_B0)
                if k is not None:
                    return ('K', k, used, st)
        if (q, c) not in tr:
            return ('H', (chr(65+q) + str(c)), used, st)
        used.add(chr(65+q) + str(c))
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return ('T', None, used, maxs)

out_lines = []
print(f"\nProfiling {len(extra_machines)} extra parents for ext9:")
for pid, grp, tag, mode, B0, nE, M, tmpl_str in extra_machines:
    t = kl.tmpl(M, tmpl_str)
    all_def = set()
    undef = []
    for q, row in enumerate(M.split('_')):
        for c in range(2):
            s = chr(65+q) + str(c)
            if row[3*c] == '-':
                undef.append(s)
            else:
                all_def.add(s)
    if not undef:
        # For intact base machines with 0 undef slots, we can test setting each B_only/E_only slot as undef!
        pass
    D_cfgs = [([3], 4, B0), ([3], 5, B0)]
    B_cfgs = [([2] + [0]*k, a, B0) for k in (1, 2, 3) for a in (5, 6)]
    E_cfgs = [([], a, B0) for a in range(6, 12)]
    D_used = set()
    for ds, a, b in D_cfgs:
        _, _, u, _ = rfk_used(M, t, ds, a, b, 50000, req_B0=B0)
        D_used |= u
    B_used = set()
    for ds, a, b in B_cfgs:
        _, _, u, _ = rfk_used(M, t, ds, a, b, 50000, req_B0=B0)
        B_used |= u
    E_used = set()
    for ds, a, b in E_cfgs:
        _, _, u, _ = rfk_used(M, t, ds, a, b, 50000, req_B0=B0)
        E_used |= u
    B_only = sorted(B_used - D_used)
    E_only = sorted(E_used - D_used - B_used)
    print(f"  {pid:18s} | U={undef} | B_only={B_only} | E_only={E_only} | {M}")
    if undef and len(M.split('_')) == 8:
        line = "\t".join([
            pid,
            "extra",
            grp,
            M,
            tmpl_str,
            str(B0),
            str(nE),
            mode,
            ",".join(undef) or "-",
            ",".join(sorted(D_used)) or "-",
            ",".join(B_only) or "-",
            ",".join(E_only) or "-",
            "-",
            "-"
        ])
        out_lines.append(line)

with open(BASE + r'\parents_extra_ext9.tsv', 'w') as f:
    for l in out_lines:
        f.write(l + '\n')
print(f"Wrote {len(out_lines)} rows to parents_extra_ext9.tsv")
