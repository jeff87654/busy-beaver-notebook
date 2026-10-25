# an_ones.py runs/<file>: for every run, ones(after the last CL) = sum of non-suffix tokens (x+1) + 2(k+1) + (3R+2) + 4 + 6t,
# and Delta = ones(HALT) - ones(after last CL);  prints Delta - 3R (expected constant per variant).
import sys, re
for r in open(sys.argv[1]).read().split('== ')[1:]:
    L = r.strip().split('\n'); lab = L[0]; J = [l for l in L if l.startswith('J')]; end = L[-1]
    if not end.startswith('HALT'): continue
    l = J[-1]; t = int(re.search(r't=(\d+)', l).group(1)); k = int(re.search(r'k=(\d+)', l).group(1)); R = int(re.search(r'R=(\d+)', l).group(1))
    toks = []
    for x in l.split('|', 1)[1].split():
        if x.startswith('z'): continue
        a, _, b = x.partition('*'); toks += [int(a)] * (int(b) if b else 1)
    # suffix = last k+1 tokens (m and the k digits); tokens before stay
    keep = toks[:len(toks) - (k + 1)]
    after = sum(x + 1 for x in keep) + 2 * (k + 1) + 3 * R + 2 + 4 + 6 * t
    H = int(re.search(r'ones (\d+)', end).group(1))
    print('%-22s t=%d k=%d R=%d  after=%d halt=%d  Delta-3R=%d   last view: ...%s' % (lab, t, k, R, after, H, H - after - 3 * R, l.split('|')[1][-40:]))
