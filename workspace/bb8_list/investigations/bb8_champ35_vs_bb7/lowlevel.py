#!/usr/bin/env python3
"""Low-level rules in the wiki's one-line format, for both machines.

Each mid-level rule starts from a B(a; ...) snapshot and consists of one or more machine-level
phases; the end of a phase is the next configuration with the head at the right end of the tape
in the snapshot state (A for the champion, G for the 8-state machine).  This script runs one phase
from the first configuration of each mid-level rule and prints the tape before and after,
together with the leftmost/rightmost blank cells the head visits (the 0^m annotations).
"""
from ligocki_notation import Sim, Family, CHAMP7, CHAMP8

ARROW = ' --> '


def one_phase(fam, a, digits):
    sim = fam.build(a, digits)
    start_pos, start_len = sim.pos, sim.r1 + 1
    before = sim.tape_str()
    lo, hi = sim.pos, sim.pos
    stop = {}

    def cb(step, s):
        if step > 0:
            stop['s'] = s
            raise StopIteration

    # track the head's excursion by stepping in small chunks
    tape = sim.tape
    try:
        while True:
            sim.run(sim.steps + 1, fam.state, cb)
            lo, hi = min(lo, sim.pos), max(hi, sim.pos)
            if sim.halted:
                break
    except StopIteration:
        pass
    after = sim.tape_str()
    # cells right of the original tape that the head visited, and cells left of it
    right_blanks = hi - start_len + 1
    left_blanks = max(0, (sim.l1 if before else start_pos) - lo)
    return before, after, right_blanks, lo, hi, sim


def show(name, fam, cases):
    print(f'\n===== {name} =====')
    for label, a, D in cases:
        before, after, rb, lo, hi, sim = one_phase(fam, a, D)
        head = f'{chr(65 + sim.state)}>' if not sim.halted else 'Z>'
        tail_note = f'   (head visits {rb} blank cell(s) right of the tape, {sim.steps} steps)'
        print(f'  {label}: B({a}; {", ".join(map(str, D))})')
        print(f'      {before} {chr(65 + fam.state)}>' + f'  0^{rb}' + ARROW + f'{after} {head}{tail_note}')


if __name__ == '__main__':
    fam7 = Family(CHAMP7, prefix='11', suffix='0011100', state=0)
    fam8 = Family(CHAMP8, prefix='', suffix='', state=6)
    for name, fam in (('BB(7) champion', fam7), ('8-state machine', fam8)):
        show(name, fam, [
            ('rule 1, first phase (3 units of the digit run -> accumulator; later phases = rounds)', 0, [1]),
            ('rule 1, first phase', 1, [1]),
            ('rule 2, k=0, first phase', 1, [0, 1]),
            ('rule 2, k=1, first phase', 1, [0, 0, 1]),
            ('rule 2, k=2, first phase', 0, [0, 0, 0, 1]),
            ('halt, k=2', 1, [0, 0]),
            ('halt, k=3', 1, [0, 0, 0]),
            ('halt, k=2, a=3', 3, [0, 0]),
        ])
