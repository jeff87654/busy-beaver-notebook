import idle
"""summ.py WORLD [WORLD2 ...]: parse runs/<world>/*.txt -> table per name with outcome, ones, jumps, level-ups,
max depth, final t, zeros.  level-ups = cleared depths > 1.15 x running max (>= 30).  With 2+ worlds: side by side."""
import sys, os, re, glob
def parse(path):
    d = dict(out='KILLED', ones='', zs=[], t=0, tops=[], nI=0)
    try: L = open(path, errors='replace').read().splitlines()
    except OSError: return None
    for l in L:
        if l.startswith('J'):
            m = re.search(r' t=(\d+)', l); d['t'] = int(m.group(1)) if m else d['t']
            if re.search(r'used=\S*I[01]', l): d['nI'] += 1
        elif l.startswith('HALT'):
            d['out'] = 'HALT ' + l.split()[1]; m = re.search(r'ones (\d+)', l); d['ones'] = m.group(1) if m else ''
        elif l.startswith('STOP'): d['out'] = 'STOP'
        elif l.startswith('END'): d['out'] = 'END'
        elif l.startswith('zeros:'): d['zs'] = [int(x) for x in l[6:].split()]
    if not d['zs']:
        d['zs'] = [int(m.group(1)) for l in L if l.startswith('J') for m in [re.search(r' k=(\d+)', l)] if m]
    mx = 0; ups = 0
    for z in d['zs']:
        if z >= 30 and z > 1.15 * mx: ups += 1
        mx = max(mx, z)
    d['ups'] = ups; d['mx'] = mx
    return d
def comp(zs):
    out = []
    for k in zs:
        if out and out[-1][0] == k: out[-1][1] += 1
        else: out.append([k, 1])
    s = ' '.join(str(k) if c == 1 else '%sx%d' % (k, c) for k, c in out)
    return s if len(s) < 110 else s[:50] + ' .. ' + s[-55:]
def table(worlds):
    names = sorted(set(os.path.basename(p)[:-4] for w in worlds for p in glob.glob('runs/%s/*.txt' % w)))
    rows = []
    for n in names:
        r = [n]
        for w in worlds:
            d = parse('runs/%s/%s.txt' % (w, n))
            r.append(None if d is None else d)
        rows.append(r)
    return rows
if __name__ == '__main__':
    ws = sys.argv[1:]
    for r in table(ws):
        cells = []
        for w, d in zip(ws, r[1:]):
            cells.append('-' if d is None else '%s|%s|u%d|t%d|I%d|%s' % (d['out'], d['ones'], d['ups'], d['t'], d['nI'], comp(d['zs'])))
        print(r[0] + '\t' + '\t'.join(cells))

def fresh(zs, lo=1000):
    n = 0; prev = None; out = []
    for z in zs:
        if z >= lo and (prev is None or (abs(z - prev) > 0.02 * prev and not (0.55 <= z / max(prev, 1) <= 0.65))):
            n += 1; out.append(z)
        prev = z
    return n, out
