"""final.py: merge reb7 stages into final verdicts, families and survivors.
  python final.py --main run_s0.jsonl,run_s1.jsonl --multi mr_main.jsonl,mr_rest.jsonl --growth growth.tsv
                  --blk blk/blk_nofit.txt --pool pool7.tsv --out final7 [--hand hand.tsv]
Stages: S1 rule fit + residue rounds (reb7), S2 multi-template rounds (mrounds), S3 NOFIT growth (literal K-trace +
template-free longest periodic block), S4 hand/subagent analyses (hand.tsv: machine \t verdict \t note).
Outputs: OUT_verdicts.tsv (one row per machine), OUT_families.tsv, OUT_survivors.tsv, printed summary."""
import idle  # noqa: F401
import argparse
import json
from collections import Counter, defaultdict


def short(v):
    if v.startswith('NOT-RECORD-CLASS'):
        return v.split(')')[0] + ')'
    return v.split('(')[0].split('+')[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--main', required=True)
    ap.add_argument('--multi', default='')
    ap.add_argument('--growth', default='')
    ap.add_argument('--blk', default='')
    ap.add_argument('--pool', default='pool7.tsv')
    ap.add_argument('--hand', default='')
    ap.add_argument('--out', default='final7')
    a = ap.parse_args()
    pool = {}
    for l in open(a.pool):
        f = l.rstrip('\n').split('\t')
        if f[0] != 'machine':
            pool[f[0]] = f
    rows = {}
    for fn in a.main.split(','):
        for l in open(fn):
            r = json.loads(l)
            rows[r['machine']] = r
    multi = {}
    for fn in [x for x in a.multi.split(',') if x]:
        for l in open(fn):
            r = json.loads(l)
            multi[r['machine']] = r
    growth = {}
    if a.growth:
        for l in open(a.growth):
            f = l.rstrip('\n').split('\t')
            growth[f[0]] = f
    blk = {}
    if a.blk:
        for l in open(a.blk):
            f = l.split()
            if len(f) >= 8:
                blk[f[0]] = (int(f[5]), int(f[6]), f[7])
    hand = {}
    if a.hand:
        for l in open(a.hand):
            f = l.rstrip('\n').split('\t')
            if len(f) >= 2 and not l.startswith('#'):
                hand[f[0]] = f[1:]
    out = {}
    for m, r in rows.items():
        v = r['verdict']
        stage = 'S1'
        note = ''
        if m in multi and not multi[m]['verdict'].startswith(('ERROR', 'NOFIT')):
            v2 = multi[m]['verdict']
            if not v.startswith('NOT-RECORD-CLASS') or v2.startswith(('HALT', 'CLASS')):
                v, stage = v2, 'S2'
                note = 'templates=%s' % multi[m].get('ntemplates')
        if (r['verdict'].startswith(('NOFIT', 'NO-K', 'ERROR'))) and m in blk:
            span, b, st = blk[m]
            g = growth.get(m, [m, '?'])[1]
            if b <= 100:
                v, stage = 'NOT-RECORD-CLASS(LOW-GROWTH)', 'S3'
                note = 'longest periodic block %d cells, span %d after 3e8 steps (%s; K-trace %s)' % (b, span, st, g)
            else:
                v, stage = 'UNSETTLED(NOFIT, grows: block %d span %d)' % (b, span), 'S3'
        if m in hand:
            v, stage = hand[m][0], 'S4'
            note = hand[m][1] if len(hand[m]) > 1 else ''
        out[m] = (v, stage, note)
    # verdict table
    with open(a.out + '_verdicts.tsv', 'w', newline='\n') as fo:
        fo.write('machine\tgrade\tsources\tverdict\tstage\tnote\ttemplate\trules\texhaustion\n')
        for m in sorted(out, key=lambda m: (short(out[m][0]), m)):
            r = rows[m]
            ex = r.get('E0') if r.get('marker') else (list((r.get('E') or {}).values()) or ['-'])[0]
            fo.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
                m, pool.get(m, ['', '', '?'])[2], pool.get(m, ['', '', '', '?'])[3], out[m][0][:160], out[m][1],
                out[m][2][:200], r.get('tmpl', r.get('tmpl_in')), (r.get('rules') or '-')[:200], (ex or '-')[:200]))
    c = Counter(short(v[0]) for v in out.values())
    cs = Counter((short(v[0]), v[1]) for v in out.values())
    print('machines', len(out))
    for k, n in c.most_common():
        print('  %5d %s' % (n, k))
    print('by stage:', dict(cs))
    # families: rules+exhaustion signature (fitted) / dlscan params (NOFIT)
    fam = defaultdict(list)
    for m, r in rows.items():
        key = r.get('sig') or ('NOFIT|' + str(r.get('tmpl_in', ''))[:40] + '|' + short(out[m][0]))
        fam[key].append(m)
    with open(a.out + '_families.tsv', 'w', newline='\n') as fo:
        fo.write('family\trep\tn\tverdicts\tstages\tmembers\trules\texhaustion_map\n')
        for i, (k, ms) in enumerate(sorted(fam.items(), key=lambda x: -len(x[1]))):
            ms = sorted(ms)
            r = rows[ms[0]]
            vs = Counter(short(out[m][0]) for m in ms)
            st = Counter(out[m][1] for m in ms)
            ex = r.get('E0') if r.get('marker') else (list((r.get('E') or {}).values()) or ['-'])[0]
            fo.write('F%d\t%s\t%d\t%s\t%s\t%s\t%s\t%s\n' % (
                i + 1, ms[0], len(ms), dict(vs), dict(st), ','.join(ms[1:]) or '-', (r.get('rules') or '-')[:220],
                (ex or '-')[:220]))
    print('families', len(fam))
    surv = [m for m, v in out.items() if not short(v[0]).startswith(('NEVER', 'NOT-RECORD'))]
    with open(a.out + '_survivors.tsv', 'w', newline='\n') as fo:
        for m in sorted(surv, key=lambda m: short(out[m][0])):
            fo.write('%s\t%s\t%s\t%s\n' % (m, out[m][0][:200], out[m][1], out[m][2][:200]))
    print('survivors', len(surv), Counter(short(out[m][0]) for m in surv))


if __name__ == '__main__':
    main()
