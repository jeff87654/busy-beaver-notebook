"""summarize.py: merge deep/broad/rerun/f141 results into final_verdicts.tsv and print tallies."""
import json, csv, collections, re, subprocess
sz = {}; fam = {}
for l in open('targets0.tsv'):
    f = l.rstrip('\n').split('\t'); sz[f[1]] = int(f[0]); fam[f[1]] = f[2]
ver = {r['machine']: r for r in csv.DictReader(open('../reb7/final_all_verdicts.tsv'), delimiter='\t')}
res = {}
for fn in ('broad.jsonl', 'broad_rerun.jsonl', 'deep.jsonl', 'deep_rerun.jsonl', 'f141.jsonl', 'f141b.jsonl'):
    try:
        for l in open(fn):
            d = json.loads(l)
            if fn == 'f141.jsonl' and 'rules not measured' in d.get('verdict', ''): continue
            res[d['machine']] = (fn, d)
    except FileNotFoundError: pass
# f3check outcome
f3 = {}
out = subprocess.run(['python', 'f3check.py'] + ['logs/%s.txt' % m for m, (fn, d) in res.items()
                      if 'halting exhaustion classes not excluded' in d.get('verdict', '')], capture_output=True, text=True).stdout
for l in out.splitlines():
    if l and not l.startswith(' '):
        f3[l.split()[0]] = l
deep = set(l.split()[0] for l in open('deep_list.txt')) | set(l.split()[0] for l in open('extra_list.txt'))
rows = []; tally = collections.Counter()
for m, (fn, d) in res.items():
    v = d.get('verdict', '')
    if m in f3 and 'CONFIRMED' in f3[m]: v = 'CONFIRMED(last-borrow parity: ' + f3[m].split('CONFIRMED(')[1]
    if m in ('1RB---_1LC0LD_1RF1RD_0RG0LE_0RF1LB_1RA0RC_0LA1RE', '1RB0RD_1RC---_1LD0LE_1RA1RE_0RG0LF_0RA1LC_0LB1RF') and fn == 'broad.jsonl':
        continue
    kind = v.split('(')[0]
    tally[(kind, 'deep' if m in deep else 'broad')] += 1
    rows.append((sz.get(m, -1), m, fam.get(m, '-'), 'deep' if m in deep else 'broad', (d.get('template') or ['-'] * 5), v,
                 d.get('rule0'), d.get('rule1'), (d.get('halt_classes') or [])[:4], d.get('lock_miss'), d.get('nK'),
                 d.get('probes'), d.get('probe_bad'), d.get('exact_fallback'), ver.get(m, {}).get('verdict', '-')[:45], d.get('secs')))
rows.sort(key=lambda r: -r[0])
with open('final_verdicts.tsv', 'w') as f:
    f.write('size\tmachine\treb7_family\tset\ttemplate(Q,side,TF,z,coding)\tverdict\tD\tB1\thalt_classes(r<NCL mod 720)\tlock_miss\tnK\tprobes\tprobe_bad\texact_fallback\treb7_verdict\tsecs\n')
    for r in rows: f.write('\t'.join(str(x) for x in r) + '\n')
print(tally)
print('rows', len(rows), 'cpu-secs (audits only)', sum((r[-1] or 0) for r in rows))
for r in rows:
    if not r[5].startswith('CONFIRMED'): print('NOT CONFIRMED', r[0], r[1], r[5][:100])
