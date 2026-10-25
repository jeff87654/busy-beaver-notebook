"""Head in state q placed at the left end of a (10)^r region followed by a T1 tail; what happens?"""
from tailvisit import T, runs
def sim(tape, p, q, maxs, stop):
    for st in range(maxs):
        r = stop(tape, p, q, st)
        if r: return r
        c = tape.get(p, 0); t = T[(q, c)]
        if t is None: return ('HALT', st)
        tape[p] = t[0]; p += t[1]; q = t[2]
    return ('timeout',)
for left in ['', '1', '11', '101', '1001']:
  for r in [6, 7]:
    for q in 'ABDEFGH':
        for start in [0, 1]:  # head on first cell of region or second
            w = left + '10' * r + '1' * 8 + '00111111' + '001001'
            tape = {i: int(c) for i, c in enumerate(w)}
            L0 = len(left); TS = L0 + 2 * r  # tail start
            def stop(tape, p, q, st):
                if p < L0: return ('exitL', q, st)
                if p >= TS: return ('tail', q, st, p - TS)
                return None
            res = sim(tape, L0 + start, q, 100000, stop)
            print(repr(left), r, q, start, res)
