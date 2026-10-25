#!/usr/bin/env python3
"""Ligocki-style B(a; b, c, ..., z) snapshots and rules, for the BB(7) champion and for the
8-state champion-rule machine 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF.

Ligocki's analysis (wiki page of the BB(7) champion) snapshots the machine when the head is in
state A on the first blank right of the tape and the run next to the accumulator is empty:

    B(a; b, c, ..., z) = 0^inf 111 (01)^(3z+1) 1 ... 1 (01)^(3b+1) 1 (01)^0 1 (01)^(3a+1) 0011100 A> 0^inf

This script applies the same convention to both machines (for the 8-state machine the fixed
blocks are PREFIX = "" and SUFFIX = "", state G), records every such snapshot on a run from the
blank tape, classifies the transitions between consecutive snapshots as Ligocki's rule 1 / rule 2
and prints the constants, and runs constructed B(a; [0]*k) configurations to the halt to get the
Halt(...) count.  Plain cell-by-cell simulation, no acceleration, no shared code with the Coq
proofs or the dlscan2 templates.
"""
import re
import sys

CHAMP7 = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF"
CHAMP8 = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF"


def parse_tm(s):
    tm = {}
    for i, row in enumerate(s.split('_')):
        for j in range(2):
            t = row[3 * j:3 * j + 3]
            if t == '---':
                tm[(i, j)] = None            # undefined: halts, counted as 1RZ for sigma
            elif t[2] == 'Z':
                tm[(i, j)] = (int(t[0]), t[1], None)
            else:
                tm[(i, j)] = (int(t[0]), t[1], ord(t[2]) - 65)
    return tm


class Sim:
    """Tape as a list with a left margin; l1/r1 track the leftmost/rightmost 1."""

    def __init__(self, tm, tape='', head=0, state=0):
        self.tm = tm
        margin = 1 << 12
        self.tape = [0] * margin + [int(c) for c in tape] + [0] * margin
        self.pos = margin + head
        self.state = state
        self.steps = 0
        self.halted = False
        ones = [i for i, c in enumerate(self.tape) if c]
        self.l1 = ones[0] if ones else len(self.tape)
        self.r1 = ones[-1] if ones else -1
        self.first_entry = {}

    def run(self, max_steps, snap_state=None, snap_cb=None):
        tape, tm = self.tape, self.tm
        pos, state, steps = self.pos, self.state, self.steps
        l1, r1 = self.l1, self.r1
        while steps < max_steps:
            if state == snap_state and pos > r1 and snap_cb is not None:
                snap_cb(steps, ''.join('1' if c else '0' for c in tape[l1:pos]))
            tr = tm[(state, tape[pos])]
            if tr is None:                      # undefined transition: standard sigma counts a 1RZ
                tape[pos] = 1
                if pos > r1:
                    r1 = pos
                if pos < l1:
                    l1 = pos
                steps += 1
                self.halted = True
                self.final_write = True
                break
            w, d, ns = tr
            tape[pos] = w
            if w:
                if pos > r1:
                    r1 = pos
                if pos < l1:
                    l1 = pos
            else:
                if pos == r1:
                    while r1 >= l1 and tape[r1] == 0:
                        r1 -= 1
                if pos == l1:
                    while l1 <= r1 and tape[l1] == 0:
                        l1 += 1
                if r1 < l1:
                    l1, r1 = len(tape), -1
            pos += 1 if d == 'R' else -1
            steps += 1
            if ns is None:
                self.halted = True
                self.final_write = False
                break
            if ns not in self.first_entry:
                self.first_entry[ns] = steps
            state = ns
            if pos >= len(tape):
                tape.extend([0] * len(tape))
            elif pos < 0:
                n = len(tape)
                tape[0:0] = [0] * n
                pos += n
                l1 += n
                r1 += n
        self.pos, self.state, self.steps = pos, state, steps
        self.l1, self.r1 = l1, r1
        return self.halted

    def ones(self):
        return sum(self.tape)

    def tape_str(self):
        if self.r1 < 0:
            return ''
        return ''.join('1' if c else '0' for c in self.tape[self.l1:self.r1 + 1])


class Family:
    """B(a; b, c, ..., z) parser/builder for one machine (Ligocki's convention)."""

    def __init__(self, tm_str, prefix, suffix, state):
        self.tm = parse_tm(tm_str)
        self.prefix, self.suffix, self.state = prefix, suffix, state
        self.rx = re.compile('^' + re.escape(prefix) + r'((?:1(?:01)*)+)' + re.escape(suffix) + '$')

    def parse(self, s):
        """Return (a, digits_nearest_first) or None.  Runs must be (01)^(3x+1); the run next to
        the accumulator must be empty."""
        m = self.rx.match(s)
        if not m:
            return None
        runs = [len(r) // 2 for r in re.findall(r'1((?:01)*)', m.group(1))]
        if len(runs) < 3 or runs[-2] != 0:
            return None
        vals = runs[:-2] + [runs[-1]]
        if any(n % 3 != 1 for n in vals):
            return None
        a = (runs[-1] - 1) // 3
        digits = [(n - 1) // 3 for n in reversed(runs[:-2])]
        return a, digits

    def build(self, a, digits):
        s = self.prefix
        for d in reversed(digits):
            s += '1' + '01' * (3 * d + 1)
        s += '1' + '1' + '01' * (3 * a + 1) + self.suffix
        return Sim(self.tm, s, head=len(s), state=self.state)


def fmt(a, digits):
    # compress runs of equal digits as [x]*k, Ligocki's notation
    out, i = [], 0
    while i < len(digits):
        j = i
        while j < len(digits) and digits[j] == digits[i]:
            j += 1
        out.append(f'[{digits[i]}]*{j - i}' if j - i >= 3 else ', '.join(str(digits[i]) for _ in range(j - i)))
        i = j
    return f'B({a}; {", ".join(out)})'


def classify(prev, cur):
    (a, D), (a2, D2) = prev, cur
    if len(D) != len(D2):
        return 'LENGTH CHANGE'
    if D and D[0] >= 1 and D2 == [D[0] - 1] + D[1:]:
        return f'rule1  a -> 2a+{a2 - 2 * a}'
    # rule 2: [0]*k, 0, n+1, rest -> [0]*k, a+c, n, rest ; accumulator -> a0
    k = 0
    while k < len(D) and D[k] == 0:
        k += 1
    # D = [0]*k ++ [n+1] ++ rest with k >= 1
    if k >= 1 and k < len(D) and D[k] >= 1 and D2 == [0] * (k - 1) + [D2[k - 1]] + [D[k] - 1] + D[k + 1:]:
        return f'rule2  k={k - 1}: writes a+{D2[k - 1] - a}, accumulator -> {a2}'
    return 'OTHER'


def blank_run(name, fam, max_steps, show=40):
    print(f'\n===== {name}: run from the blank tape, {max_steps} steps, Ligocki-style snapshots =====')
    snaps = []

    def cb(step, s):
        p = fam.parse(s)
        if p is not None:
            snaps.append((step, p))

    sim = Sim(fam.tm)
    sim.run(max_steps, fam.state, cb)
    print('first entry into each state (step):', {chr(65 + q): s for q, s in sorted(sim.first_entry.items())})
    print(f'{len(snaps)} snapshots; first {show}:')
    last = None
    first_all_ones = None
    for i, (step, p) in enumerate(snaps):
        rule = classify(last[1], p) if last else 'START'
        if first_all_ones is None and p[1] and all(d == 1 for d in p[1]):
            first_all_ones = (step, p)
        if i < show or i >= len(snaps) - 3:
            print(f'  step {step:>9}: {fmt(*p):<60} {rule}')
        elif i == show:
            print('  ...')
        last = (step, p)
    if first_all_ones:
        print(f'first all-ones digit list: step {first_all_ones[0]}: {fmt(*first_all_ones[1])}')
    rules = {}
    last = None
    for step, p in snaps:
        if last:
            r = classify(last, p)
            rules[r] = rules.get(r, 0) + 1
        last = p
    print('rule tally over consecutive snapshots:', rules)
    return snaps


def rule_grid(name, fam, a_values, max_steps=5_000_000):
    print(f'\n===== {name}: rules from constructed configurations =====')
    for a in a_values:
        for D in ([1], [2], [0, 1], [0, 2], [0, 0, 1], [0, 0, 0, 1], [1, 2, 0, 1]):
            sim = fam.build(a, D)
            got = []

            def cb(step, s):
                p = fam.parse(s)
                if p is not None and step > 0:
                    got.append((step, p))
                    raise StopIteration

            try:
                sim.run(max_steps, fam.state, cb)
            except StopIteration:
                pass
            if got:
                step, p = got[0]
                print(f'  {fmt(a, D):<28} -> {fmt(*p):<36} in {step:>7} steps   {classify((a, D), p)}')
            else:
                print(f'  {fmt(a, D):<28} -> no snapshot within {max_steps} steps (halted={sim.halted})')


def halt_grid(name, fam, a_values, k_values, max_steps=50_000_000):
    print(f'\n===== {name}: B(a; [0]*k) to the halt =====')
    print('  ones = ones on the tape when the machine halts; +1 if the halting transition is undefined (counted as 1RZ)')
    for k in k_values:
        for a in a_values:
            sim = fam.build(a, [0] * k)
            n0 = sim.ones()
            halted = sim.run(max_steps)
            if not halted:
                print(f'  B({a}; [0]*{k}): no halt within {max_steps} steps')
                continue
            print(f'  B({a}; [0]*{k}): halts after {sim.steps:>7} steps, ones {n0} -> {sim.ones()}'
                  f'   final tape {sim.tape_str()[:90]}{"..." if len(sim.tape_str()) > 90 else ""}')


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    fam7 = Family(CHAMP7, prefix='11', suffix='0011100', state=0)
    fam8 = Family(CHAMP8, prefix='', suffix='', state=6)
    if which in ('all', '7'):
        blank_run('BB(7) champion', fam7, 2_000_000)
        rule_grid('BB(7) champion', fam7, [0, 1, 2, 3, 5])
        halt_grid('BB(7) champion', fam7, [0, 1, 2, 3, 4], [1, 2, 3])
    if which in ('all', '8'):
        blank_run('8-state machine', fam8, 2_000_000, show=50)
        rule_grid('8-state machine', fam8, [0, 1, 2, 3, 5])
        halt_grid('8-state machine', fam8, [0, 1, 2, 3, 4, 5], [1, 2, 3])
