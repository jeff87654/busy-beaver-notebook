"""Watch the start-up of a champion-type machine: the tape, compressed into (01)^k / (10)^k runs, each time
the head stands on a blank beyond either end of the written region.

  python trace_startup.py MACHINE [MAXSTEP=7000] [EVERY=1]

Lines: step, state, side (L/R), compressed tape with the head marked.  EVERY > 1 prints only every n-th
end event (the first and last are always printed).
"""
from __future__ import annotations

import re
import sys

ST = 'ABCDEFGH'


def parse(m):
    t = {}
    for i, row in enumerate(m.split('_')):
        for c in range(2):
            x = row[3 * c:3 * c + 3]
            t[(i, c)] = None if x in ('---',) or x[2] == 'Z' else (int(x[0]), 1 if x[1] == 'R' else -1, ST.index(x[2]))
    return t


def compress(s):
    """Greedy run-length: (01)^k for k >= 2 written as 01^k, other cells as is."""
    out, i = [], 0
    while i < len(s):
        m = re.match(r'(?:01){2,}', s[i:])
        if m:
            k = len(m.group(0)) // 2
            out.append(f'(01)^{k}')
            i += 2 * k
        else:
            out.append(s[i])
            i += 1
    # merge adjacent single characters
    res, buf = [], ''
    for t in out:
        if len(t) == 1:
            buf += t
        else:
            if buf:
                res.append(buf)
                buf = ''
            res.append(t)
    if buf:
        res.append(buf)
    return ' '.join(res)


def main():
    m = sys.argv[1]
    maxstep = int(sys.argv[2]) if len(sys.argv) > 2 else 7000
    every = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    tm = parse(m)
    tape, pos, q = {}, 0, 0
    lo = hi = 0
    events = []
    for step in range(1, maxstep + 1):
        s = tape.get(pos, 0)
        tr = tm[(q, s)]
        if tr is None:
            events.append((step, 'HALT', pos))
            break
        w, d, q = tr
        if w:
            tape[pos] = 1
        else:
            tape.pop(pos, None)
        pos += d
        ones = tape.keys()
        if tape:
            l1, r1 = min(ones), max(ones)
        else:
            l1, r1 = pos, pos
        if pos > r1 or pos < l1:
            side = 'R' if pos > r1 else 'L'
            a, b = min(l1, pos), max(r1, pos)
            cells = ''.join('1' if tape.get(i, 0) else '0' for i in range(a, b + 1))
            k = pos - a
            events.append((step, ST[q], side, cells[:k], cells[k:]))
    for i, e in enumerate(events):
        if e[1] == 'HALT':
            print(f'{e[0]:>6} HALT')
            continue
        if i % every and i != len(events) - 1:
            continue
        step, q, side, left, right = e
        print(f'{step:>6} {q} {side}  {compress(left)} [{q}] {compress(right)}')


if __name__ == '__main__':
    main()
