import idle, sys
from tm import TM
# slotuse.py MACHINE N : count reads of each slot; first few step numbers of each
m = sys.argv[1]; N = int(sys.argv[2])
M = TM(m); cnt = {}; first = {}
while M.steps < N:
    k = chr(65+M.q) + str(M.t.get(M.pos, 0))
    cnt[k] = cnt.get(k, 0) + 1
    first.setdefault(k, []).append(M.steps) if len(first.get(k, [])) < 6 else None
    if not M.step(): print('HALT', M.steps, M.halted); break
for k in sorted(cnt): print(k, cnt[k], first[k])
