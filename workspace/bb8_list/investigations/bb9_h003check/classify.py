import idle
"""classify.py FILES..: group exit-survey rows by endgame route: key (first orbit value < 60), the two tokens before the ESC
digit 7 (the parked-list clear = first CL with X = 7 and K >= 500), ESC depth mod 5, the post-ESC CL pattern (X shown
as offsets from the ESC accumulator class: 'T' = X >= 500), counter use, outcome, bad events."""
import sys, re
from collections import defaultdict
groups = defaultdict(list)
for fn in sys.argv[1:]:
    for line in open(fn):
        if not line.startswith(('h003', 'M8')): continue
        m = re.search(r' K=(\d+) .*?\| (HALT \S+|MAXS|NONE)[^|]*\| bad=(\d+) \| ncl=(\d+) L0=(\d+) keyL0=(\d+) .*?\| (.*)$', line.strip())
        if not m: continue
        K, out, bad, key, comp = int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(6)), m.group(7).split()
        esc = None
        for i, c in enumerate(comp):
            if c == 'CNT': continue
            X, k = map(int, c.split('/'))
            if X == 7 and k >= 500: esc = i; break
        if esc is None:
            sig = (key, 'noESC', out); groups[sig].append((K, bad)); continue
        Pesc = int(comp[esc].split('/')[1])
        post = []
        for c in comp[esc + 1:]:
            if c == 'CNT': post.append('CNT'); continue
            X, k = map(int, c.split('/'))
            post.append(('T' if X >= 500 else str(X)) + '/' + ('P' if abs(k - Pesc) < 60 else str(k)))
        # collapse repeats
        cp = []
        for p in post:
            if cp and cp[-1][0] == p: cp[-1][1] += 1
            else: cp.append([p, 1])
        pat = ' '.join(p if n == 1 else '%s x%d' % (p, n) for p, n in cp)
        sig = (key, 'Pesc%%5=%d' % (Pesc % 5), pat, out)
        groups[sig].append((K, bad))
for sig in sorted(groups, key=lambda s: (s[0], str(s[1:]))):
    v = groups[sig]
    print('%-4s %-9s n=%-3d bad=%d | %s | K e.g. %s' % (sig[0], sig[1], len(v), sum(b for _, b in v), ' | '.join(sig[2:]), [k for k, _ in v[:5]]))
