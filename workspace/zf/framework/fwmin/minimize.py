"""Moore partition refinement on a TM table: states with identical (write,dir,next-class) for both symbols merge."""
import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\framework\fwmin')
from tmfast import load
start, tbl = load(sys.argv[1])
S = sorted({s for s, _ in tbl})
cls = {s: 0 for s in S}
while True:
    sig = {s: tuple((tbl[(s, r)][0], tbl[(s, r)][1], cls.get(tbl[(s, r)][2], tbl[(s, r)][2])) if (s, r) in tbl else None for r in '01') for s in S}
    keys = {}
    new = {s: keys.setdefault((cls[s], sig[s]), len(keys)) for s in S}
    if len(keys) == len(set(cls.values())): break
    cls = new
groups = {}
for s in S: groups.setdefault(cls[s], []).append(s)
print('states', len(S), 'classes', len(groups))
for g in groups.values():
    if len(g) > 1: print(g)
