"""iso.py M1 M2...: for each machine vs the first, best state relabelling (M -> first) and the transitions that differ."""
import sys, itertools
def parse(m): 
    r = m.split('_'); return [[r[i][0:3], r[i][3:6]] for i in range(len(r))]
S = 'ABCDEFG'
A = parse(sys.argv[1])
for m in sys.argv[2:]:
    B = parse(m); best = None
    for p in itertools.permutations(range(7)):
        # p[i] = index in A of B's state i
        diff = []
        for i in range(7):
            for c in range(2):
                tb = B[i][c]; ta = A[p[i]][c]
                tbm = tb if tb == '---' else tb[0:2] + S[p[S.index(tb[2])]]
                if tbm != ta: diff.append(f'{S[i]}{c}:{tb}->{tbm} vs {S[p[i]]}{c}:{ta}')
        if best is None or len(diff) < len(best[1]): best = (p, diff)
    p, diff = best
    print(m, 'map', ''.join(S[p[i]] for i in range(7)), 'start->', S[p[0]], 'ndiff', len(diff), diff)
