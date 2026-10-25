"""nearmiss.py: rank lit-mode output lines (run with --keep 0) by passed starts + matched fraction of failed starts."""
import sys
rows = []
for l in open(sys.argv[1]):
    if '|' not in l: continue
    head, prof = l.split('|', 1); p = head.split()
    toks = prof.split(); npass = toks.count('P'); fr = 0.0; fails = []
    for i, t in enumerate(toks):
        if '/' in t:
            a, b = t.rstrip('h').split('/'); f = int(a) / max(1, int(b)); fr += f; fails.append('s%d:%s' % (i, t))
    rows.append((npass + fr, npass, p[0], p[1], ' '.join(fails)))
rows.sort(reverse=True)
k = int(sys.argv[2]) if len(sys.argv) > 2 else 10
for r in rows[:k]: print('%.2f pass=%d %s %s fails: %s' % r)
