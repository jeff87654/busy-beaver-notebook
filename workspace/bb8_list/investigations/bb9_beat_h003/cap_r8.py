import sys
from solve_rounds import load
caps = [0, 12, 24, 120]
maps = {c: {tm: tab for _, _, tm, tab in load('capN_%d.txt' % c)} for c in caps}
targets = [tm for tm in maps[0] if tm.endswith('_---1RI_1RA0LF') or tm.endswith('_---1RI_0RE0LF')]
for tm in targets:
    print(tm)
    bad_kind = []; bad_I = []; ddl = {}
    for k in range(20, 201):
        cells = [maps[c][tm][k] for c in caps]
        kinds = {x[0] for x in cells}
        if len(kinds) > 1:
            bad_kind.append((k, [x[0] for x in cells])); continue
        if cells[0][0] != 'KK':
            continue
        Is = {x[3] for x in cells}
        if len(Is) > 1:
            bad_I.append(k)
        d = tuple(x[1] - cells[0][1] for x in cells)
        ddl.setdefault(d, []).append(k)
    print('  kind changes:', bad_kind[:10], 'count', len(bad_kind))
    print('  I changes:', bad_I[:10], 'count', len(bad_I))
    for d, ks in sorted(ddl.items(), key=lambda x: -len(x[1]))[:8]:
        print('  dL shift (cap0,12,24,120)=%s  n=%d  mod6=%s  e.g. k=%s' % (d, len(ks), tuple(x % 6 for x in d), ks[:8]))
