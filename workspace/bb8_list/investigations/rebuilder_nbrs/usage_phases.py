"""Which transitions does each phase of a champion-rule machine use?

  python usage_phases.py

For each parent (dlscan2 template, orientation R): the start-up from the blank tape up to the first family
configuration, the digit rules R1-R3 on constructed configurations (each run until the exact successor
predicted by the rules), and the empty / all-zero list case R4 (run until the next family configuration or
a halt).  A neighbour can keep R1-R3 only if it leaves their transitions alone, and can change the
rebuild only by changing a transition that R4 uses; this fixes the targeted radius-2 search.

Template (dlscan2 form, digits farthest first):
  K(ds; a; b) = P  u^(al d1 + be) s ... u^(al dn + be) s  u^(al a + be) s  u^(alB b + beB)  S  Q>0
"""
from __future__ import annotations

import re
from collections import Counter

ST = 'ABCDEFGHIJKLMNOP'   # up to 16 states (9-state roots since 2026-10-05)

PARENTS = {
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1RF': ('G', '11', '01', '1', 3, 1, 3, 1, '101'),
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1RH': ('G', '11', '01', '1', 3, 1, 3, 1, '101'),
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0LH0RF_---1RE': ('B', '11', '10', '1', 3, 1, 3, 2, '111001'),
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0RH0RF_---1LE': ('B', '11', '10', '1', 3, 1, 3, 2, '111001'),
    # references with a halting R4
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF': ('G', '1', '01', '1', 3, 1, 3, 1, '10101'),
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF_------': ('B', '11', '10', '1', 3, 1, 3, 2, '111001'),
}


def parse_tm(s):
    t = {}
    for i, row in enumerate(s.split('_')):
        for c in range(2):
            x = row[3 * c:3 * c + 3]
            t[(i, c)] = None if x == '---' else (int(x[0]), 1 if x[1] == 'R' else -1, ST.index(x[2]))
    return t


class Tmpl:
    def __init__(self, q, P, u, s, al, be, alB, beB, S):
        self.q = ST.index(q)
        self.P, self.u, self.s, self.S = P, u, s, S
        self.al, self.be, self.alB, self.beB = al, be, alB, beB
        body = f'((?:{re.escape(u)})*)'
        self.rx = re.compile('^' + re.escape(P) + f'((?:{body}{re.escape(s)})*)' + body + re.escape(S) + '$')

    def build(self, ds, a, b):
        x = self.P
        for d in ds:
            x += self.u * (self.al * d + self.be) + self.s
        x += self.u * (self.al * a + self.be) + self.s + self.u * (self.alB * b + self.beB) + self.S
        return x

    def parse(self, x):
        m = self.rx.match(x)
        if not m:
            return None
        lu = len(self.u)
        runs = [len(r) // lu for r in re.findall(f'((?:{re.escape(self.u)})*){re.escape(self.s)}', m.group(1))]
        nb = len(m.group(3)) // lu
        if not runs or (nb - self.beB) % self.alB or nb < self.beB:
            return None
        vals = []
        for n in runs:
            if (n - self.be) % self.al or n < self.be:
                return None
            vals.append((n - self.be) // self.al)
        return tuple(vals[:-1]), vals[-1], (nb - self.beB) // self.alB


def run(tm, T, tape_str, target=None, cap=3_000_000, stop_any=False):
    """Run from tape_str with the head on the blank right of it in state T.q.  Stops at `target`
    (ds, a, b), at any family configuration if stop_any, at a halt, or after cap steps.
    Returns (outcome, steps, usage Counter, final family config or None)."""
    tape = {i: int(c) for i, c in enumerate(tape_str) if c == '1'}
    pos, q, use = len(tape_str), T.q, Counter()
    hi = max(tape) if tape else -1          # rightmost 1, maintained incrementally
    for step in range(1, cap + 1):
        s = tape.get(pos, 0)
        tr = tm[(q, s)]
        use[f'{ST[q]}{s}'] += 1
        if tr is None:
            return 'HALT', step, use, None
        w, d, nq = tr
        if w:
            tape[pos] = 1
            if pos > hi:
                hi = pos
        elif s:
            del tape[pos]
            if pos == hi:
                hi = max(tape) if tape else -1
        pos += d
        q = nq
        # head on a blank right of the word; the word may end in up to 3 zeros (units like 010)
        if q == T.q and tape and hi < pos <= hi + 4:
            l = min(tape)
            x = ''.join('1' if tape.get(i, 0) else '0' for i in range(l, pos))
            k = T.parse(x)
            if k is not None and (stop_any or k == target):
                return 'FAMILY', step, use, k
    return 'CAP', cap, use, None


def analyse(m, spec):
    tm, T = parse_tm(m), Tmpl(*spec)
    print(f'\n=== {m}   template {spec}')
    # start-up from the blank tape: first family configuration with a list of >= 2 digits
    tape, pos, q, use = {}, 0, 0, Counter()
    first = None
    for step in range(1, 200_000):
        s = tape.get(pos, 0)
        tr = tm[(q, s)]
        if tr is None:
            break
        use[f'{ST[q]}{s}'] += 1
        w, d, q = tr[0], tr[1], tr[2]
        if w:
            tape[pos] = 1
        else:
            tape.pop(pos, None)
        pos += d
        if q == T.q and tape and pos == max(tape) + 1:
            x = ''.join('1' if tape.get(i, 0) else '0' for i in range(min(tape), pos))
            k = T.parse(x)
            if k is not None and len(k[0]) >= 2:
                first = (step, k)
                break
    U0 = set(use)
    if first:
        ds = first[1][0]
        print(f'  start-up: K({len(ds)} digits {ds[:3]}..{ds[-3:]}; {first[1][1]}; {first[1][2]}) at step {first[0]}')
    print(f'  start-up uses {sorted(U0)}')
    # R1-R3 on constructed configurations, until the predicted successor
    U13, bad = Counter(), []
    probes = []
    for b in range(0, 4):
        for a in (1, 2, 3):
            probes.append(((2, 1), a, b, ((2, 1), a - 1, 2 * b + 2)))           # R1
        probes.append(((1, 2), 0, b, ((1, 1), 2 * b + 2, 0)))                    # R2
        for k in (1, 2, 3):
            ds = (1, 2) + (0,) * k
            probes.append((ds, 0, b, ((1, 1, 2 * b + 2) + (0,) * (k - 1), 0, 0)))  # R3
    for ds, a, b, tgt in probes:
        out, st, use, _ = run(tm, T, T.build(ds, a, b), target=tgt)
        U13.update(use)
        if out != 'FAMILY':
            bad.append((ds, a, b, out))
    print(f'  R1-R3 probes: {len(probes)}, failures {bad[:3]}')
    print(f'  R1-R3 use {sorted(U13)}')
    # R4: empty and all-zero lists
    U4 = Counter()
    for n in (0, 1, 2, 3):
        for b in range(0, 6):
            out, st, use, k = run(tm, T, T.build((0,) * n, 0, b), stop_any=True, cap=5_000_000)
            U4.update(use)
            desc = (f'K({len(k[0])} digits {k[0][:2]}..{k[0][-2:]}; {k[1]}; {k[2]})' if k else '')
            if b in (0, 1, 5) and n in (0, 3):
                print(f'  R4 K(0^{n}; 0; {b}): {out} after {st} steps {desc}')
    print(f'  R4 uses {sorted(U4)}')
    only4 = sorted(set(U4) - set(U13))
    unused = sorted(f'{ST[i]}{c}' for i in range(8) for c in range(2) if f'{ST[i]}{c}' not in set(U0) | set(U13) | set(U4))
    print(f'  used by R4 but not R1-R3: {only4}')
    print(f'  used by none of start-up/R1-R4: {unused}')
    return set(U0), set(U13), set(U4)


if __name__ == '__main__':
    for m, spec in PARENTS.items():
        analyse(m, spec)
