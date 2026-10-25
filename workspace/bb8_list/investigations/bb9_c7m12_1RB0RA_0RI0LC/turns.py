"""Literal run printing the tape at every direction change (or every step with --all), with head and state.
  python turns.py MACHINE WORD HEAD STATE MAXSTEPS"""
import sys

m, word, head, st, mx = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
allsteps = '--all' in sys.argv
tr = {}
for i, g in enumerate(m.split('_')):
    for c in (0, 1):
        x = g[3 * c:3 * c + 3]
        tr[(chr(65 + i), c)] = None if x[0] == '-' else (int(x[0]), 1 if x[1] == 'R' else -1, x[2])
tape = {i: int(ch) for i, ch in enumerate(word)}
pos, q, lastd = head, st, 0
lo, hi = 0, max(len(word) - 1, head)


def show(step):
    s = ''
    for i in range(lo, hi + 1):
        s += (f'[{q}]' if i == pos else '') + str(tape.get(i, 0))
    print(f'{step:6d} {s}')


show(0)
for step in range(1, mx + 1):
    c = tape.get(pos, 0)
    t = tr[(q, c)]
    if t is None:
        print('HALT', step)
        show(step)
        break
    w, d, nq = t
    tape[pos] = w
    if d != lastd or allsteps:
        show(step - 1)
    lastd = d
    pos += d
    q = nq
    lo, hi = min(lo, pos), max(hi, pos)
