"""classify.py OUTDIR [OUTDIR...]: parse sweep res.txt files -> per-child records + interesting rows.
A child line: MACHINE OUTCOME ... J=.. X=.. esc=.. maxk=.. step=.. vstep=.. zeros=[..] escJ=[..]
Escalations after the snapshot = esc - snap.nesc.  Interesting: HALT with esc_after >= 2, or non-HALT with esc_after >= 3.
"""
import sys, json, os, re


def parse(l):
    f = l.split()
    if len(f) < 2:
        return None
    r = {'m': f[0], 'out': f[1]}
    if f[1] == 'HALT':
        r['slot'] = f[2]
    for x in f:
        if '=' in x:
            k, v = x.split('=', 1)
            if k in ('J', 'X', 'esc', 'maxk', 'step', 'ones', 'width'):
                try:
                    r[k] = int(v)
                except ValueError:
                    pass
            elif k == 'vstep':
                r[k] = float(v)
    m = re.search(r'zeros=\[([^\]]*)\]', l)
    r['zeros'] = m.group(1) if m else ''
    m = re.search(r'escJ=\[([^\]]*)\]', l)
    r['escJ'] = m.group(1) if m else ''
    return r


def load(d):
    s = json.load(open(os.path.join(d, 'summary.json')))
    recs = []
    p = os.path.join(d, 'res.txt')
    if os.path.exists(p):
        for l in open(p):
            r = parse(l)
            if r and r['out'] in ('HALT', 'T', 'JMAX', 'XMAX', 'RCAP'):
                recs.append(r)
    return s, recs


def main():
    for d in sys.argv[1:]:
        s, recs = load(d)
        e0 = s['snap']['nesc'] if isinstance(s.get('snap'), dict) else 0
        cnt = {}
        inter = []
        for r in recs:
            ea = r.get('esc', 0) - e0
            key = '%s+%d' % (r['out'], ea)
            cnt[key] = cnt.get(key, 0) + 1
            if (r['out'] == 'HALT' and ea >= 2) or (r['out'] != 'HALT' and ea >= 3):
                inter.append((ea, r))
        print('==', d, s.get('base'), s.get('X'), s.get('mode'), 'n=%s' % s.get('n'), 'snap', s.get('snap'))
        print('  ', ' '.join('%s:%d' % kv for kv in sorted(cnt.items())))
        inter.sort(key=lambda x: (-x[0], x[1]['out']))
        for ea, r in inter[:30]:
            print('   esc+%d %s %s %s J=%s X=%s maxk=%s zeros=[%s]' % (ea, r['out'], r.get('slot', ''), r['m'], r.get('J'), r.get('X'),
                                                                      r.get('maxk'), r['zeros'][-80:]))


if __name__ == '__main__':
    main()
