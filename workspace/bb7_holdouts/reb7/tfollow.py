"""tfollow.py: literal follow-up of exhaustions that leave the template (reb7 'T' outcomes).
  python tfollow.py IN.jsonl[,IN2.jsonl] OUT.tsv [--steps 300000000]
For every row whose rounds end in T: rebuild the exhaustion configuration K(0^n; 0; b) (n = exhaustion level:
nE for marker templates, the list length at the start for others; P empty: n = 0) for b in a small set of
representatives of the T class (b = c mod p, b in 40..~120) and run it literally (fl7.exe), recording every
K-configuration in the template whose list length changes, and a halt."""
import idle  # noqa: F401
import json
import os
import re
import subprocess
import sys

FL7 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fl7.exe')


def targs(t):
    f = t.split(',')
    d = {}
    for x in f[2:]:
        k, v = x.split('=', 1)
        d[k] = v
    al, be = d['d'].split('d+')
    aB, bB = d['b'].split('b+')
    return [f[0], f[1], d['P'], d['u'], d['s'], al, be, aB, bB, d['S']]


def follow(m, t, n, b, steps, maxout=40):
    inp = '%s 0 %d\n' % (','.join(['0'] * n) if n else '-', b)
    p = subprocess.run([FL7, m] + targs(t) + [str(steps), str(maxout)], input=inp, capture_output=True, text=True,
                       creationflags=0x40, timeout=7200)
    return p.stdout.strip().splitlines()


def main():
    ins = sys.argv[1].split(',')
    out = sys.argv[2]
    steps = 300000000
    if '--steps' in sys.argv:
        steps = int(sys.argv[sys.argv.index('--steps') + 1])
    done = set()
    if os.path.exists(out):
        done = set(l.split('\t')[0] for l in open(out))
    rows = []
    for fn in ins:
        for l in open(fn):
            r = json.loads(l)
            rq = r.get('rounds') or {}
            v = str(rq.get('80640', [''])[0])
            if "'T'" in v or v.startswith('T@') or 'T:' in str(rq.get('80640', ['', []])[1]):
                rows.append(r)
    with open(out, 'a', newline='\n') as fo:
        for r in rows:
            m = r['machine']
            if m in done:
                continue
            t = r['tmpl']
            marker = r.get('marker')
            if t.split(',')[2] == 'P=-':
                n = 0
            elif marker:
                n = r.get('nE', 0)
            else:
                n = r['last_K'][2]
            tr = r['rounds']['80640'][1]
            cls = None
            for x in tr:
                if isinstance(x, list) and len(x) == 3 and isinstance(x[2], list):
                    for b in x[2]:
                        mm = re.match(r'T:class (\d+)', b)
                        if mm:
                            cls = int(mm.group(1))
            Es = r.get('E0') if marker else (list(r.get('E', {}).values()) or ['-'])[0]
            mp = re.match(r'mod (\d+)', Es or '')
            p = int(mp.group(1)) if mp else 1
            bs = [b for b in range(40, 40 + 2 * p + 2) if cls is None or b % p == cls][:3]
            res = []
            for b in bs:
                lines = follow(m, t, n, b, steps)
                ks = [x for x in lines if x.startswith('K')]
                end = lines[-1] if lines else '?'
                res.append('b=%d: %d K-lens [%s] end %s' % (b, len(ks), ' '.join(x.split()[2] + '@' + x.split()[1] for x in ks[:8]), end))
            fo.write('%s\t%s\tn=%d\tclass=%s mod %d\t%s\n' % (m, t, n, cls, p, ' || '.join(res)))
            fo.flush()
            print(m, res, flush=True)


if __name__ == '__main__':
    main()
