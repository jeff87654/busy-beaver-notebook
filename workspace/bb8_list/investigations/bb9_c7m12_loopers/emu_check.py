"""emu_check.py MACHINES_FILE: blank tape -> K(1^11;1;2) (head in B on the blank right of the word)?"""
import sys
from tm import parse, kword
target = kword([1] * 11, 1, 2)
def check(m, maxs=40000):
    T, n = parse(m)
    tape = {}; pos = 0; q = 0
    for step in range(maxs):
        if q == 1 and tape.get(pos, 0) == 0 and tape:
            hi = max(tape)
            if pos == hi + 1 and hi - min(tape) + 1 == len(target):
                lo = min(tape)
                if ''.join('1' if tape.get(i) else '0' for i in range(lo, hi + 1)) == target:
                    return step
        c = tape.get(pos, 0); t = T.get((q, c))
        if t is None: return f'HALT{step}'
        w, d, nq = t
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d; q = nq
    return 'NO'
if __name__ == '__main__':
    for l in open(sys.argv[1]):
        m = l.split()[0]
        print(m, check(m), flush=True)
