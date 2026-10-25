#!/usr/bin/env python3
"""Cross-checks for ligocki_notation.py:
  1. the literal simulator reproduces BB(4) and BB(5);
  2. the BB(7) champion's tape at steps 2117 (the Kc snapshot of the champ35 report) and 8178
     (the wiki's "Start at step 8178: B(2, [1]*12)"), and the 8-state machine's at 6397;
  3. rule 1 for larger accumulators (a = 60, 100);
  4. end-to-end: small B(a; digits) starts run literally to the halt, compared with the
     abstract mid-level rules + Halt formula (constants as measured by ligocki_notation.py).
"""
from ligocki_notation import Sim, Family, parse_tm, fmt, CHAMP7, CHAMP8


def check_bb(name, tm_str, steps_expected, ones_expected):
    sim = Sim(parse_tm(tm_str))
    sim.run(10 ** 9)
    print(f'  {name}: halted={sim.halted} steps={sim.steps} ones={sim.ones()}  '
          f'expected {steps_expected}/{ones_expected}  {"OK" if (sim.steps, sim.ones()) == (steps_expected, ones_expected) else "MISMATCH"}')


def tape_at(tm_str, step):
    sim = Sim(parse_tm(tm_str))
    sim.run(step)
    s = sim.tape_str()
    rel = sim.pos - sim.l1
    if 0 <= rel <= len(s):
        shown = s[:rel] + f' {chr(65 + sim.state)}> ' + s[rel:]
    else:
        shown = s + f'   (head at offset {rel} in state {chr(65 + sim.state)})'
    return shown


def abstract_run(a, digits, c1, c2, a0):
    """Ligocki's mid-level rules until the list is all zero; digits nearest-first.
    rule1: (a; b+1, ...) -> (a+a+c1; b, ...);  rule2: (a; 0^k, 0, n+1, ...) -> (a0; 0^k, a+c2, n, ...)."""
    D = list(digits)
    n_rules = 0
    while any(D):
        if D[0] > 0:
            D[0] -= 1
            a = 2 * a + c1
        else:
            k = 0
            while D[k] == 0:
                k += 1
            D[k] -= 1
            D[k - 1] = a + c2
            a = a0
        n_rules += 1
    return a, n_rules


def end_to_end(name, fam, cases, c1, c2, a0, halt):
    print(f'\n===== {name}: literal run to the halt vs abstract rules =====')
    for a, D in cases:
        sim = fam.build(a, D)
        halted = sim.run(2_000_000_000)
        af, nr = abstract_run(a, D, c1, c2, a0)
        pred = halt(af, len(D))
        print(f'  {fmt(a, D):<20} literal: halted={halted} steps={sim.steps:>10} ones={sim.ones():>6}   '
              f'abstract: final a={af:>6} ({nr} rule applications) Halt={pred:>6}   {"OK" if pred == sim.ones() else "MISMATCH"}')


if __name__ == '__main__':
    print('===== simulator sanity: BB(4), BB(5) champions =====')
    check_bb('BB(4)', '1RB1LB_1LA0LC_1RZ1LD_1RD0RA', 107, 13)
    check_bb('BB(5)', '1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA', 47176870, 4098)

    print('\n===== tapes at the quoted steps =====')
    for step in (2117, 2154, 8178, 8574):
        print(f'  BB(7) champion, step {step}:\n    {tape_at(CHAMP7, step)}')
    for step in (6397, 6413):
        print(f'  8-state machine, step {step}:\n    {tape_at(CHAMP8, step)}')

    fam7 = Family(CHAMP7, prefix='11', suffix='0011100', state=0)
    fam8 = Family(CHAMP8, prefix='', suffix='', state=6)

    print('\n===== rule 1 with larger accumulators =====')
    for name, fam in (('BB(7) champion', fam7), ('8-state machine', fam8)):
        for a in (60, 100):
            sim = fam.build(a, [1])
            got = []

            def cb(step, s, fam=fam, got=got):
                p = fam.parse(s)
                if p is not None and step > 0:
                    got.append((step, p))
                    raise StopIteration

            try:
                sim.run(10 ** 9, fam.state, cb)
            except StopIteration:
                pass
            print(f'  {name}: {fmt(a, [1])} -> {fmt(*got[0][1])} in {got[0][0]} steps')

    end_to_end('BB(7) champion', fam7,
               [(0, [1]), (2, [1]), (0, [2]), (0, [0, 1]), (1, [0, 1]), (2, [0, 1]), (0, [1, 1])],   # (0,[0,0,1]) would reach a = 2^16-4: too slow literally
               c1=4, c2=2, a0=0, halt=lambda a, k: 3 * a + 2 * k + 10)
    end_to_end('8-state machine', fam8,
               [(1, [1]), (5, [1]), (1, [2]), (1, [0, 1]), (2, [0, 1]), (3, [0, 1]), (1, [1, 1]), (0, [0, 0, 1])],
               c1=3, c2=1, a0=1, halt=lambda a, k: 12 * a + 2 * k + 23)
