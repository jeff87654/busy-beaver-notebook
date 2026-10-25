"""The start-up's rebuild as a function of the seed.

The 35-digit machine's start-up reaches X(0) = 0^inf 1 (01)^7 1 (01)^2 G> at step 197 and then
X(35) = 0^inf 1 (01)^7 (101)^35 1 (01)^2 G> at step 6397 (= Kc(2, 0^34; 0; 0)).  This script starts machines
on the seed configuration  S(c) = 0^inf 1 (01)^c 1 (01)^2 G>  for c = 1..CMAX and runs them to the first
configuration of the form  0^inf 1 (01)^x (101)^Z 1 (01)^2 G>  (any x, Z), or a halt.

  python seed_fn.py MACHINE [CMAX=20] [CAP=50000000]

Prints c, outcome, x (the leading run), Z (the number of 101 blocks), and steps.
"""
from __future__ import annotations

import re
import sys

ST = 'ABCDEFGH'
RX = re.compile(r'^1((?:01)*)((?:101)*)10101$')


def parse(m):
    t = {}
    for i, row in enumerate(m.split('_')):
        for c in range(2):
            x = row[3 * c:3 * c + 3]
            t[(i, c)] = None if x == '---' or x[2] == 'Z' else (int(x[0]), 1 if x[1] == 'R' else -1, ST.index(x[2]))
    return t


def run_from(tm, tape_str, q, cap, nmatch=1):
    """Run until the nmatch-th X-shaped configuration; returns (outcome, step, (x, Z)) of the last one, and
    the list of all matches seen as (step, x, Z)."""
    seen = []
    tape = {i: 1 for i, ch in enumerate(tape_str) if ch == '1'}
    pos = len(tape_str)
    hi = max(tape) if tape else -1
    for step in range(1, cap + 1):
        s = tape.get(pos, 0)
        tr = tm[(q, s)]
        if tr is None:
            return 'HALT', step, None, seen
        w, d, q = tr
        if w:
            tape[pos] = 1
            if pos > hi:
                hi = pos
        elif s:
            del tape[pos]
            if pos == hi:
                hi = max(tape) if tape else -1
        pos += d
        if q == 6 and tape and pos == hi + 1:
            lo = min(tape)
            x = ''.join('1' if tape.get(i, 0) else '0' for i in range(lo, pos))
            m = RX.match(x)
            if m:
                seen.append((step, len(m.group(1)) // 2, len(m.group(2)) // 3))
                if len(seen) == nmatch:
                    return 'X', step, seen[-1][1:], seen
    return 'CAP', cap, None, seen


def main():
    m = sys.argv[1]
    cmax = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 50_000_000
    tm = parse(m)
    print(f'machine {m}')
    out, st, r, seen = run_from(tm, '', 0, 20000, nmatch=4)
    print('  from blank:', ' -> '.join(f'X(x={x},Z={z})@{t}' for t, x, z in seen))
    for c in range(1, cmax + 1):
        out, st, r, seen = run_from(tm, '1' + '01' * c + '10101', 6, cap, nmatch=2)
        print(f'  S(c={c:>2}): ' + ' -> '.join(f'X(x={x},Z={z})@{t}' for t, x, z in seen) + ('' if out == 'X' else f'  [{out} at {st}]'))


if __name__ == '__main__':
    main()
