"""Check closed-form step counts against every step count recorded by check_rules.py (check_rules.json)."""
import json
d = json.load(open('check_rules.json'))
F = {
    'R1': lambda m: 30 + 8 * m,
    'R3': lambda j: 38 + 16 * j,
    'Y4': lambda j: 36 + 16 * j,
    'Y3': lambda j: 79 + 16 * j,
    'Y1': lambda j: 65 + 16 * j,
    'Pstep': lambda j, t, s: 72 * j * j + 274 * j + 254,
    'P00': lambda j: 72 * j * j + 274 * j + 254,
    'Y4f': lambda j: 72 * j * j + 226 * j + 174,
    'Y3f': lambda j: 79 + 16 * j,
    'P01': lambda j: 81 + 16 * j,
}
tot = bad = 0
for name, f in F.items():
    for k, v in d[name]['steps'].items():
        args = [int(x) for x in str(k).split(',')]
        tot += 1
        if f(*args) != v:
            bad += 1
            print('MISMATCH', name, k, v, f(*args))
print('%d step counts checked, %d mismatches' % (tot, bad))
