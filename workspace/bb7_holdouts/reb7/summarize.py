"""summarize.py: verdict counts, families (by rule+E signature), survivors from reb7 jsonl outputs.
  python summarize.py OUT1.jsonl [OUT2.jsonl ...] [--pool pool7.tsv] [--fam fam.tsv] [--surv surv.tsv]"""
import json
import sys
from collections import Counter, defaultdict

args = [a for a in sys.argv[1:] if not a.startswith('--')]
opts = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--') and '=' in a)
pool = {}
for l in open(opts.get('pool', 'pool7.tsv')):
    f = l.rstrip('\n').split('\t')
    if f[0] != 'machine':
        pool[f[0]] = f
rows = {}
for fn in args:
    for l in open(fn, encoding='utf-8'):
        try:
            r = json.loads(l)
        except Exception:
            continue
        rows[r['machine']] = r


def vclass(r):
    v = r.get('verdict', '?')
    if v.startswith('NOT-RECORD-CLASS'):
        return v.split(')')[0] + ')'
    return v.split('(')[0].split('+')[0]


c = Counter(vclass(r) for r in rows.values())
print('rows', len(rows), 'of pool', len(pool))
for k, n in c.most_common():
    print('  %5d  %s' % (n, k))
fam = defaultdict(list)
for m, r in rows.items():
    fam[r.get('sig') or ('NOSIG:' + vclass(r) + ':' + m)].append(m)
print('families (signatures):', len(fam))
if 'fam' in opts:
    with open(opts['fam'], 'w', newline='\n', encoding='utf-8') as fo:
        fo.write('rep\tmembers\tn\tverdict\tgrowth\tnE\ttemplate\trules\tE\trounds_Q1\n')
        for sig, ms in sorted(fam.items(), key=lambda x: (vclass(rows[x[1][0]]), -len(x[1]))):
            ms = sorted(ms)
            r = rows[ms[0]]
            rq = r.get('rounds', {}).get('80640', ['-'])[0] if r.get('rounds') else '-'
            fo.write('%s\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
                ms[0], ','.join(ms[1:]) or '-', len(ms), r.get('verdict', '?')[:140], r.get('growth', '-'),
                r.get('nE', '-'), r.get('tmpl', r.get('tmpl_in')), (r.get('rules') or '-')[:300],
                (r.get('E0') if r.get('marker') else str(r.get('E'))) or '-', str(rq)[:120]))
surv = [r for r in rows.values() if not vclass(r).startswith(('NEVER-HALTS', 'NOT-RECORD-CLASS'))]
print('survivors (not NEVER / NOT-RECORD):', len(surv), Counter(vclass(r) for r in surv))
if 'surv' in opts:
    with open(opts['surv'], 'w', newline='\n', encoding='utf-8') as fo:
        for r in sorted(surv, key=lambda r: vclass(r)):
            fo.write('%s\t%s\t%s\t%s\n' % (r['machine'], r.get('tmpl', r.get('tmpl_in')), r.get('verdict', '?')[:200],
                                             pool.get(r['machine'], ['', '', '?'])[2]))
