"""Differential checks of resumable RLE search simulation against two oracles."""
import json
import random
from sim import simulate
from search3 import run


def literal(table, limit):
    tape, head, state = set(), 0, 0
    for steps in range(1, limit+1):
        w, d, state = table[state][int(head in tape)]
        if w:
            tape.add(head)
        else:
            tape.discard(head)
        head += d
        if state == -1:
            return 'halt', steps, len(tape)
    return 'steps', limit, len(tape)


if __name__ == '__main__':
    rng = random.Random(2026092601)
    counts = {'fixtures':1000, 'rle_matches':0, 'literal_halters':0,
              'resumed_matches':0}
    for i in range(counts['fixtures']):
        table = [[(rng.randrange(2), rng.choice((-1,1)), rng.randrange(-1,8))
                  for symbol in range(2)] for state in range(8)]
        expected = simulate(table, max_ops=500)
        actual = run(table, 500)
        assert actual[:4] == expected, (i, table, actual, expected)
        counts['rle_matches'] += 1
        scalar = literal(table, 5000)
        if scalar[0] == 'halt':
            assert actual[:3] == scalar, (i, table, actual, scalar)
            counts['literal_halters'] += 1
        elif actual[0] == 'halt' and actual[1] <= 5000:
            raise AssertionError((i, table, actual, scalar))
        split = run(table, 500, stop_on_entry=5)
        if split[0] == 'entry':
            snapshot = split[-1]
            before = repr(snapshot)
            rest = run(table, 500-split[3], initial=snapshot)
            assert rest[:3] == actual[:3], (i, table, rest, actual)
            assert repr(snapshot) == before, 'Resuming mutated shared snapshot'
            assert rest[3] + split[3] == actual[3]
            counts['resumed_matches'] += 1
    with open('audit_search3.json','w') as f:
        json.dump(counts,f,indent=2)
    print(json.dumps(counts,indent=2))
