"""collect.py SCRDIR [T2DIR] [T3DIR] : merge tiers -> final outcome per child; ranked table of interesting children.

Final outcome of a child = its line in the highest tier where it was run.  E = total escalations (world count),
Ea = escalations after the snapshot.  Interesting: HALT with E >= 3, or non-HALT with E >= 4 at the last tier.
Writes SCRDIR/../collect_<name>.tsv and prints counts.
"""
import sys, os, json, glob, re, collections


def parse(l):
    f = l.split()
    if len(f) < 2 or f[0].startswith('#'):
        return None
    r = {'m': f[0], 'out': f[1], 'line': l.strip()}
    if f[1] == 'HALT':
        r['slot'] = f[2]
    for x in f:
        if '=' in x:
            k, v = x.split('=', 1)
            if k in ('J', 'X', 'esc', 'maxk', 'ones', 'step'):
                try:
                    r[k] = int(v)
                except ValueError:
                    pass
    m = re.search(r'zeros=\[([^\]]*)\]', l)
    r['zeros'] = m.group(1) if m else ''
    return r


def main():
    scr = sys.argv[1]
    tiers = [scr] + sys.argv[2:]
    summ = {}
    for f in glob.glob(os.path.join(scr, '[0-9][0-9][0-9].json')):
        o = json.load(open(f))
        summ[o['i']] = o
    final = {}
    for t, d in enumerate(tiers):
        for i, o in summ.items():
            for run in o.get('runs', []):
                if 'file' not in run:
                    continue
                p = os.path.join(d, run['file'])
                if not os.path.exists(p):
                    continue
                for l in open(p):
                    r = parse(l)
                    if not r or r['out'] not in ('HALT', 'T', 'JMAX', 'XMAX', 'ESCMAX', 'WIDE', 'RCAP', 'LOOP'):
                        continue
                    r['tier'] = t + 1; r['i'] = i; r['X'] = run['X']; r['c'] = run['c']; r['e0'] = run['snap']['nesc']
                    r['base'] = o['m']
                    final[(r['m'], run['c'])] = r
    cnt = collections.Counter()
    inter = []
    for k, r in final.items():
        E = r.get('esc', 0); Ea = E - r['e0']
        cnt[(r['tier'], r['out'], min(E, 9))] += 1
        if (r['out'] == 'HALT' and E >= 3) or (r['out'] not in ('HALT', 'LOOP') and E >= 4):
            inter.append((r['out'] == 'HALT', E, r))
    for k, v in sorted(cnt.items()):
        print('tier%d %-7s E=%d : %d' % (k[0], k[1], k[2], v))
    inter.sort(key=lambda x: (-x[0], -x[1]))
    name = os.path.basename(os.path.normpath(scr))
    with open(os.path.join(os.path.dirname(os.path.normpath(scr)) or '.', 'collect_%s.tsv' % name), 'w') as fo:
        fo.write('halt\tE\tEa\ttier\tout\tslot\tchild\tbase_i\tX\tcls\tJ\tXreads\tmaxk\tones\tzeros\n')
        for h, E, r in inter:
            fo.write('%d\t%d\t%d\t%d\t%s\t%s\t%s\t%d\t%s\t%d\t%s\t%s\t%s\t%s\t%s\n' % (
                h, E, E - r['e0'], r['tier'], r['out'], r.get('slot', ''), r['m'], r['i'], r['X'], r['c'], r.get('J'),
                r.get('X'), r.get('maxk'), r.get('ones', ''), r['zeros'][-100:]))
    print('interesting:', len(inter), ' halting with E>=3:', sum(1 for x in inter if x[0]))
    for h, E, r in inter[:25]:
        print(' ', 'HALT' if h else r['out'], 'E=%d' % E, r['m'], 'zeros=[%s]' % r['zeros'][-70:])


if __name__ == '__main__':
    main()
