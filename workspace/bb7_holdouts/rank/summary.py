"""summary.py RANK.tsv : compact fixed-width table of a rank7 output (for REPORT.txt / quick looks)."""
import idle  # noqa: F401
import sys

rows = [ln.rstrip('\n').split('\t') for ln in open(sys.argv[1], encoding='utf-8')]
H = rows[0]
ix = {c: i for i, c in enumerate(H)}


def g(r, c):
    return r[ix[c]] if ix[c] < len(r) else '-'


print('%-3s %-49s %-8s %-30s %6s %-12s %-26s %s' % ('#', 'machine', 'grade', 'verdict (rank7)', 'level', 'halts', 'first K (step n)', 'settled / note'))
for r in rows[1:]:
    fk = g(r, 'first_K')
    fk_s = fk.split(' ds=')[0].replace('step ', '') if fk != '-' else '-'
    note = g(r, 'settled')
    if note == '-':
        n = g(r, 'notes')
        r2 = g(r, 'round2')
        note = ('round2: ' + r2.split(': ')[-1]) if r2 not in ('-', '') else n[:60]
    print('%-3s %-49s %-8s %-30s %6s %-12s %-26s %s' % (g(r, 'rank'), g(r, 'machine'), g(r, 'grade'), g(r, 'verdict')[:30],
                                                      g(r, 'est_level'), g(r, 'halts')[:12], fk_s, note[:70]))
