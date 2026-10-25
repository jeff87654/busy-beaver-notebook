"""Recognize an elementary, provably nonhalting expanding-sweep family.

At t_n = 4*n*n + 2*n, the machine is in A at -2*n and its tape is
exactly 1 on [-2*n+1, 2*n]. The six-rule sweep takes 8*n+6 steps
to the same form for n+1. All other transitions are unreachable.
"""
import json
from sim import parse


def recognize(machine):
    table = parse(machine)
    if len(table) < 4:
        return None
    if table[0][0] != (1, 1, 1):
        return None
    if table[1][1] != (1, 1, 1):
        return None
    b0 = table[1][0]
    if b0 is None or b0[:2] != (1, 1):
        return None
    x = b0[2]
    if x < 0 or x >= len(table) or table[x][0] != (1, -1, 3):
        return None
    if table[3] != [(1, -1, 0), (1, -1, 3)]:
        return None
    return chr(65+x)


def check_initial_cycles(machine, cycles=10):
    table = parse(machine)
    tape, head, state, steps = set(), 0, 0, 0
    for n in range(cycles+1):
        target = 4*n*n + 2*n
        while steps < target:
            write, direction, state = table[state][int(head in tape)]
            if write:
                tape.add(head)
            else:
                tape.discard(head)
            head += direction
            steps += 1
        assert state == 0 and head == -2*n
        assert tape == set(range(-2*n+1, 2*n+1))


if __name__ == '__main__':
    with open('run2_merged.json') as f:
        data = json.load(f)
    results = []
    for machine in sorted({x[1] for x in data['unresolved']}):
        x = recognize(machine)
        assert x is not None
        check_initial_cycles(machine)
        results.append({'machine':machine, 'intermediate_state':x,
                        'classification':'proved nonhalting',
                        'cycle_time':'t(n) = 4*n*n + 2*n',
                        'ones_at_cycle':'4*n'})
    with open('audit_unresolved.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f'All {len(results)} unique unresolved machines match the proved expanding-sweep family.')
