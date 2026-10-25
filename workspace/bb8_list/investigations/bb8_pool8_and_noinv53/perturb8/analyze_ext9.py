import collections, re

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

rows = load_tsv('scan_ext9_cls53.tsv')
print(f"Total ext9 cls53 survivor rows: {len(rows)}")

pstats = collections.Counter()
epats = collections.Counter()
by_epat_grp = collections.defaultdict(list)

for r in rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    pstats[cat] += 1
    epats[epat] += 1
    by_epat_grp[(epat, grp, cat)].append(r)

print("\npstats:", dict(pstats))
print("epats:", dict(epats))

print("\n=== BREAKDOWN BY (epat, grp, cat) ===")
for (epat, grp, cat), items in sorted(by_epat_grp.items()):
    # Find item with largest nE or maxL
    best = max(items, key=lambda x: (int(re.search(r'nE=(\d+)', x[6]).group(1)), int(re.search(r'maxL=(\d+)', x[6]).group(1))))
    print(f"  {epat} | {grp:14s} | {cat:13s} | count={len(items):4d} | best: {best[0]} {best[2]} {best[6]} {best[7]}")
    print(f"    tm={best[3]}")
    print(f"    det={best[8][:130]}")
