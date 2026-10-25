"""ana.py: analyse mini-follower histories (mf_GH.tsv / mg80_GH.tsv format): growth of k, non-zero token count (k - zeros),
events; print candidates.  usage: python ana.py FILE [--min-growth G] [--kind K]"""
import sys, re, argparse
ap = argparse.ArgumentParser(); ap.add_argument('file'); ap.add_argument('--min-growth', type=float, default=30)
ap.add_argument('--kind', default=None); ap.add_argument('--all', action='store_true'); a = ap.parse_args()
rx = re.compile(r'J k=(\d+) far=(\w+) ev=(\w+) zeros=(\d+) r=([\d,]+)')
rows = []
for l in open(a.file):
    f = l.rstrip('\n').split('\t')
    if len(f) < 5: continue
    m, kind, n, bj, hist = f[:5]
    js = rx.findall(hist)
    ks = [int(x[0]) for x in js]; zs = [int(x[3]) for x in js]; evs = [x[2] for x in js]; far = [x[1] for x in js]
    nz = [k - z for k, z in zip(ks, zs)]
    last = hist.split(' ; ')[-1]
    rows.append((m, kind, ks, zs, nz, evs, far, last))
nsel = 0
for m, kind, ks, zs, nz, evs, far, last in rows:
    if a.kind and kind != a.kind: continue
    if len(ks) < 4: continue
    growth = (ks[-1] - ks[3]) / max(1, len(ks) - 3)
    if growth < a.min_growth and not a.all: continue
    nzdrop = nz[3] - nz[-1]
    nsel += 1
    print(f'{m}\t{kind}\tn={len(ks)}\tgrowth/stage={growth:.1f}\tk:{ks[0]}..{ks[-1]}\tnz:{nz[:4]}..{nz[-4:]}\tdrop={nzdrop}\tev={"".join(e[0] for e in evs)}\tfar={"".join(x[0] for x in far)}\t{last[:60]}')
print('selected', nsel, 'of', len(rows), file=sys.stderr)
