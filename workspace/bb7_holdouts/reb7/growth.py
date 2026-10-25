"""growth.py: literal growth evidence for rows the rule fitter could not model (NOFIT / NO-K).
  python growth.py IN.jsonl[,IN2] OUT.tsv
Literal run from the blank tape in the dlscan template (rk7 trace, 1e9 steps, 20000 K-configs): number of K-configs,
max list length, max a, max b, and the dlscan2 R1/R2 slopes (from the pool's dl3 params). A row is LOW-GROWTH when
max(a, b) < 200 and the list length < 40 after 3e8 steps (an f_omega engine reaches accumulators in the thousands
within 1e8 steps: BB(7) champion b=4094 at 2e8, X33 b~5000 at 1e7)."""
import idle  # noqa: F401
import json
import os
import sys
import fit7

DL = {}
for f in ('../dl3_hits/out.tsv', '../dl3_triage7/out.tsv', 'dl3_c.tsv',
          '../../bb8_list/investigations/bb9_triage7_and_1RB1LA/new_dl3_out.tsv'):
    for l in open(f):
        x = l.rstrip('\n').split('\t')
        if len(x) > 6:
            DL.setdefault(x[0], x[6])


def main():
    ins = sys.argv[1].split(',')
    out = sys.argv[2]
    done = set(l.split('\t')[0] for l in open(out)) if os.path.exists(out) else set()
    rows = [json.loads(l) for fn in ins for l in open(fn)]
    with open(out, 'a', newline='\n') as fo:
        for r in rows:
            if r['machine'] in done or not (r['verdict'].startswith(('NOFIT', 'NO-K', 'ERROR'))):
                continue
            P = fit7.Prober(r['machine'], r['tmpl_in'])
            ks, end = P.trace(300000000, 5000)
            mxa = max([k[2] for k in ks] or [0])
            mxb = max([k[3] for k in ks] or [0])
            mxn = max([len(k[1]) for k in ks] or [0])
            mxd = max([max(k[1]) if k[1] else 0 for k in ks] or [0])
            low = (max(mxa, mxb, mxd) < 200 and mxn < 40)
            fo.write('%s\t%s\t%d\t%d\t%d\t%d\t%d\t%s\t%s\t%s\n' % (
                r['machine'], 'LOW-GROWTH' if low else 'GROWS', len(ks), mxn, mxa, mxb, mxd, ' '.join(end or []),
                DL.get(r['machine'], '-')[:80], r['tmpl_in']))
            fo.flush()
            print(r['machine'], 'LOW' if low else 'GROWS', len(ks), mxn, mxa, mxb, mxd, end, flush=True)


if __name__ == '__main__':
    main()
