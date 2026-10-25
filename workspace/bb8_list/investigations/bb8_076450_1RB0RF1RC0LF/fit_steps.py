"""Fit exact step-count formulas (quadratic in k) to the literal rule checks."""
import json
from fractions import Fraction as Fr
d = json.load(open('check_rules_steps.json'))
def fit(pts):
    # quadratic through first three points, then verify all
    (x0, y0), (x1, y1), (x2, y2) = pts[:3]
    import itertools
    # Lagrange -> coefficients
    A = [[x0*x0, x0, 1], [x1*x1, x1, 1], [x2*x2, x2, 1]]
    Y = [y0, y1, y2]
    # solve 3x3
    M = [[Fr(v) for v in row] + [Fr(y)] for row, y in zip(A, Y)]
    for i in range(3):
        p = next(r for r in range(i, 3) if M[r][i] != 0); M[i], M[p] = M[p], M[i]
        for r in range(3):
            if r != i:
                f = M[r][i] / M[i][i]; M[r] = [a - f * b for a, b in zip(M[r], M[i])]
    c = [M[i][3] / M[i][i] for i in range(3)]
    ok = all(c[0]*x*x + c[1]*x + c[2] == y for x, y in pts)
    return c, ok
out = {}
for name, tab in d.items():
    if ',' in next(iter(tab)):
        bya = {}
        for key, s in tab.items():
            a, k = map(int, key.split(','))
            bya.setdefault(a, []).append((k, s))
        forms = set()
        allok = True
        for a, pts in sorted(bya.items()):
            pts.sort(); c, ok = fit(pts); allok &= ok; forms.add(tuple(c))
        print(name, '| a-independent:', len(forms) == 1, '| exact on all points:', allok, '| steps(k) =', ' + '.join('%s*%s' % (v, t) for v, t in zip(next(iter(forms)), ('k^2', 'k', '1'))))
    else:
        pts = sorted((int(k), s) for k, s in tab.items())
        c, ok = fit(pts)
        print(name, '| exact on all points:', ok, '| steps(k) =', ' + '.join('%s*%s' % (v, t) for v, t in zip(c, ('k^2', 'k', '1'))))
