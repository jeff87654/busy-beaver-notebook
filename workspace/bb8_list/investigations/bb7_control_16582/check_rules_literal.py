"""Independent literal check (no acceleration, no shared code with symsim.py) of
the rules R1, T1, R2, T2 on small parameter values, including the untouched
tail (10)^t 1101.

beta (x,j,k,t) = [A0] 0 (100)^x 1010 (100)^j 1010 (110)^k 10100 (10)^t 1101
gamma(x,j,m,t) = [A0] 0 (100)^x 1010 (100)^j 10   (100)^m 00100 (10)^t 1101
"""
import itertools, json, sys

TMS = "1RB1LD_1RC0RF_0LA0RA_0LA0LE_1LA0LG_0LA---_1RD1LG"
T = []
for ch in TMS.split('_'):
    row = []
    for i in (0, 3):
        e = ch[i:i + 3]
        row.append(None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, 'ABCDEFG'.index(e[2])))
    T.append(row)


def beta(x, j, k, t):
    return '0' + '0' + '100' * x + '1010' + '100' * j + '1010' + '110' * k + '10100' + '10' * t + '1101'


def gamma(x, j, m, t):
    return '0' + '0' + '100' * x + '1010' + '100' * j + '10' + '100' * m + '00100' + '10' * t + '1101'


def run_rule(start, target, t=0, max_steps=10_000_000):
    """start/target: strings whose first char is the head cell (state A).
    The target must be reached with the head at the left end of the used tape.
    Tapes are compared after aligning the RIGHT end (the tail never moves)."""
    tape = [int(c) for c in start]
    pad = 4000
    tape = [0] * pad + tape + [0] * 50
    pos = pad
    st = 0
    right_end = len(tape) - 50  # index just past the last start cell
    tail_len = None
    tgt = target
    maxpos = pos
    for n in range(1, max_steps + 1):
        tr = T[st][tape[pos]]
        if tr is None:
            return {'ok': False, 'why': 'halt', 'steps': n}
        w, d, ns = tr
        tape[pos] = w
        pos += d
        st = ns
        if pos > maxpos:
            maxpos = pos
        if pos < 5:
            return {'ok': False, 'why': 'ran off pad', 'steps': n}
        if st == 0 and tape[pos] == 0 and not any(tape[pos - 5:pos]):
            # head at left end in A reading 0; compare with target aligned at right end
            seg = ''.join(map(str, tape[right_end - len(tgt):right_end]))
            if right_end - len(tgt) == pos and seg == tgt and not any(tape[:pos]):
                return {'ok': True, 'steps': n, 'max_offset_from_right_end': maxpos - right_end, 'max_head_minus_tail_start': maxpos - (right_end - (2 * t + 4))}
    return {'ok': False, 'why': 'step limit', 'steps': max_steps}


results = {'R1': [], 'T1': [], 'R2': [], 'T2': []}
bad = 0
cases = 0
for x in range(1, 9):
    for j in range(0, 6):
        for t in range(0, 4):
            for k in range(0, 4):
                r = run_rule(beta(x, j, k + 1, t), beta(2 * x + 3, j + 2, k, t), t)
                cases += 1
                bad += not r['ok']
                results['R1'].append(((x, j, k, t), r))
                r = run_rule(gamma(x, j, k + 1, t), gamma(2 * x + 3, j + 2, k, t), t)
                cases += 1
                bad += not r['ok']
                results['R2'].append(((x, j, k, t), r))
            r = run_rule(beta(x, j, 0, t), gamma(2 * x + 3, 0, j + 1, t + 1), t)
            cases += 1
            bad += not r['ok']
            results['T1'].append(((x, j, t), r))
            r = run_rule(gamma(x, j, 0, t), beta(2 * x + 3, 0, j, t), t)
            cases += 1
            bad += not r['ok']
            results['T2'].append(((x, j, t), r))
summary = {}
for name, lst in results.items():
    oks = [r for p, r in lst if r['ok']]
    fails = [(p, r) for p, r in lst if not r['ok']]
    summary[name] = {'cases': len(lst), 'ok': len(oks), 'fails': fails[:5],
                     'max_head_minus_tail_start': max(r['max_head_minus_tail_start'] for r in oks) if oks else None,
                     'max_steps_per_rule': max(r['steps'] for r in oks) if oks else None}
print(json.dumps(summary, indent=1))
print('total cases', cases, 'failures', bad)
json.dump(summary, open('check_rules_literal.json', 'w'), indent=1)
