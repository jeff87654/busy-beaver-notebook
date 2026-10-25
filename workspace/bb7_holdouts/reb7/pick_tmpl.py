"""pick_tmpl.py: for machines without a dlscan grade, try the candidate templates listed by dlscan2 (prefilter
'templates' column) and keep the first one on which fit7.fit_rules succeeds and the literal trace has K-configs."""
import idle  # noqa
import sys
import fit7
cands = {}
for l in open(r'..\prefilter\hits_dl2_1M.tsv'):
    f = l.rstrip('\n').split('\t')
    if len(f) > 6:
        cands[f[0]] = f[6].split(';')
ms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
with open(sys.argv[2], 'w', newline='\n') as fo:
    fo.write('machine\ttemplate\tgrade\tsources\tcls\n')
    for m in ms:
        got = None
        tried = 0
        for t in cands.get(m, [])[:40]:
            tried += 1
            P = fit7.Prober(m, t)
            try:
                R = fit7.fit_rules(P)
            except Exception:
                continue
            ks, end = P.trace(30000000, 200)
            if len(ks) >= 20:
                got = t
                break
        fo.write('%s\t%s\t%s\tprefilter\t-\n' % (m, got or (cands.get(m, ['-'])[0]), 'PF-FIT' if got else 'PF-NOFIT'))
        fo.flush()
        print(m, got, tried, flush=True)
