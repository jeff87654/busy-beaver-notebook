"""Where could the machine halt?  Literal runs from X(z,n) = 0^inf B>0^z (10)^n 11111 0^inf for
configurations outside the invariant family (z even, or n odd).  Not needed for the proof."""
from lit import T
def run(word, limit=10**6):
    tape = {i: 1 for i, s in enumerate(word) if s}; pos = 0; q = 'B'
    for step in range(1, limit + 1):
        tr = T[(q, tape.get(pos, 0))]
        if tr is None: return 'HALT at step %d' % step
        w, d, q = tr
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d
    return 'no halt within %d' % limit
for z in range(3, 13):
    print('X(%d,0):' % z, run([0]*z + [1]*5, 10**5))
for z in (3, 7, 19):
    print('X(%d,1):' % z, run([0]*z + [1, 0] + [1]*5, 10**5))
