"""Independent literal checks of the three rules of 1RB0LD_0LC0RB_1RA1LC_0LH1RE_1LF0RF_0RB0LG_0RD0LD_1LE---.

Family (plain binary, head E reading the blank cell just left of the first block, blank beyond both ends):
    P(a1,b1,a2,b2,t) = 0^inf [E0] (10)^a1 11 0^b1 (10)^a2 11 0^b2 (10)^t 11 0^inf
Rules:
    R1: P(a1, b+2, c, d, t)   -> P(a1+1, b+1, c, d, t)
    R2: P(a+1, 1, c, d+2, t)  -> P(1, 2a+2, c+1, d+1, t)
    R3: P(a+1, 1, c, 1, t)    -> P(1, 2, a, 2c+3, t+1)
Each instance is run with no acceleration from the left-hand side until the right-hand side appears
exactly (whole tape, head E on the blank cell left of the first block, blank beyond).  The check is made
at every time the head is in state E on a blank cell with only blank cells to its left; intermediate
visits of that kind that are not the target are counted (the carry rules R2/R3 pass through one,
0^inf [E0] 1000 ...).  No run may halt.
"""
import json
import sys

TM = "1RB0LD_0LC0RB_1RA1LC_0LH1RE_1LF0RF_0RB0LG_0RD0LD_1LE---"
Q = "ABCDEFGH"


def parse(tm):
    t = []
    for ch in tm.split('_'):
        row = []
        for i in (0, 3):
            e = ch[i:i + 3]
            row.append(None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, Q.index(e[2])))
        t.append(row)
    return t


T = parse(TM)
E = Q.index('E')


def P(a1, b1, a2, b2, t):
    return '10' * a1 + '11' + '0' * b1 + '10' * a2 + '11' + '0' * b2 + '10' * t + '11'


def run_rule(lhs, rhs, max_steps=10 ** 7):
    pad = 64
    tape = bytearray(pad) + bytearray(int(c) for c in lhs) + bytearray(pad)
    pos = pad - 1  # blank cell just left of the first block
    q = E
    lo = pos  # leftmost cell ever visited
    steps = 0
    visits = 0
    while steps < max_steps:
        s = tape[pos]
        tr = T[q][s]
        if tr is None:
            return dict(ok=False, why='halt', steps=steps)
        w, d, q = tr
        tape[pos] = w
        pos += d
        steps += 1
        if pos < 0:
            tape = bytearray(pad) + tape
            pos += pad
            lo += pad
        if pos >= len(tape):
            tape += bytearray(pad)
        lo = min(lo, pos)
        if q == E and tape[pos] == 0 and not any(tape[:pos]):
            content = bytes(tape[pos + 1:]).rstrip(b'\x00')
            got = ''.join(str(x) for x in content)
            visits += 1
            if got == rhs:
                return dict(ok=True, steps=steps, visits=visits)
            if visits > 3:
                return dict(ok=False, why='too many left-end E visits', steps=steps, got=got, want=rhs)
    return dict(ok=False, why='step limit', steps=steps)


def main():
    res = {}
    total = bad = 0
    maxsteps = 0
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    cases = {
        'R1': [((a1, b + 2, c, d, t), (a1 + 1, b + 1, c, d, t))
               for a1 in range(N) for b in range(N) for c in range(4) for d in range(4) for t in range(3)],
        'R2': [((a + 1, 1, c, d + 2, t), (1, 2 * a + 2, c + 1, d + 1, t))
               for a in range(N) for c in range(N) for d in range(4) for t in range(3)],
        'R3': [((a + 1, 1, c, 1, t), (1, 2, a, 2 * c + 3, t + 1))
               for a in range(N) for c in range(N) for t in range(N)],
    }
    for name, cs in cases.items():
        ok = 0
        for lhs, rhs in cs:
            r = run_rule(P(*lhs), P(*rhs))
            total += 1
            maxsteps = max(maxsteps, r['steps'])
            if r['ok']:
                ok += 1
            else:
                bad += 1
                print('FAIL', name, lhs, rhs, r)
        res[name] = dict(cases=len(cs), passed=ok)
        print(name, ok, '/', len(cs))
    res['total'] = total
    res['failed'] = bad
    res['max_steps_single_instance'] = maxsteps
    print(json.dumps(res))
    json.dump(res, open('check_rules_literal.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
