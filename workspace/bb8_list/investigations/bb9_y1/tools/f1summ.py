# f1summ.py TSV : summarize the F1 screen.  Per variant: set of classes with IMM halts, LATE halts, RUN.
# A class-robust candidate would have no IMM in any class (and must still halt later in every class).
import sys, collections
rows = [l.rstrip('\n').split('\t') for l in open(sys.argv[1]) if l.strip()]
pat = collections.Counter(); robust = []
for r in rows:
    m, cl = r[0], [x.split('=', 1) for x in r[1:]]
    sig = ''.join('I' if v.startswith('IMM') else 'L' if v.startswith('LATE') else '.' for _, v in cl)
    pat[(m[-11:-8], sig)] += 1          # H1 slot + per-class pattern
    if 'I' not in sig: robust.append((m, sig, [v for _, v in cl if v.startswith('LATE')]))
print('classes order:', ' '.join(n for n, _ in [x.split('=', 1) for x in rows[0][1:]]))
print('pattern counts (H1, I=IMM halt, L=late halt, .=no halt in 2e6 steps):')
for k, c in sorted(pat.items()): print('  ', k[0], k[1], c)
print('variants with no IMM halt in any class: %d' % len(robust))
for m, sig, late in robust:
    if 'L' in sig: print('  LATE-HALTER', m, sig, late)
print('  (the rest never halt within the budget in any class)' if robust else '')
