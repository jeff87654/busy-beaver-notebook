"""feat.py G6TSV...: features per row: status, spanN, ratio span(N)/span(N/10), nblocks (RLE tokens with exp>=3), exps"""
import sys, re, math
for fn in sys.argv[1:]:
    for l in open(fn):
        f = l.rstrip('\n').split('\t')
        if len(f) < 9: continue
        m, st, t, s1, s2, s3, fu, q, r = f[:9]
        s2, s3 = int(s2), int(s3)
        exps = [int(x) for x in re.findall(r'\^(\d+)', r)]
        big = [e for e in exps if e >= 3]
        ratio = s3 / s2 if s2 else 0
        print(f"{m}\t{st}\t{s3}\t{ratio:.2f}\t{len(big)}\t{len(set(big))}\t{max(exps) if exps else 0}\t{r[:150]}")
