# independent spot check of the F89 subagent's odd-template rules (my own encoder/decoder + lit.exe 'ends')
import random, subprocess, re
LIT = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\never_audit\src\lit.exe'
M = '1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE'
from dec import cells
def enc(l): return 'D000' + ''.join('1' + '01' * d for d in l)
def decode(s):
    s = s.strip('0')
    if not s.startswith('1'): return None
    out = []; i = 0
    while i < len(s):
        if s[i] != '1': return None
        i += 1; d = 0
        while s.startswith('01', i): d += 1; i += 2
        out.append(d)
    return out
def rule(l):
    if len(l) == 1: return [1] * (l[0] + 2)
    if l[1] >= 3: return [l[0] + 4, l[1] - 2] + l[2:]
    k = 1
    while k + 1 < len(l) and l[k + 1] == 1: k += 1
    if k + 1 == len(l): return [1] * (k - 1) + [l[0] + 4]
    return [1] * k + [l[0] + 4, l[k + 1] - 2] + l[k + 2:]
rng = random.Random(5); bad = 0; n = 0
for it in range(150):
    L = rng.randint(1, 6)
    l = [rng.choice([1, 1, 1, 3, 5, 7, 9, 15, 31]) for _ in range(L)]
    if rng.random() < .3: l = [rng.choice([1, 3, 5, 9])] + [1] * rng.randint(1, 12) + ([rng.choice([3, 5, 7])] if rng.random() < .6 else [])
    exp = rule(l)
    p = subprocess.run([LIT, 'ends', M, '20000000', 'D', 'L', '400', enc(l)], capture_output=True, text=True)
    got = None
    for line in p.stdout.splitlines():
        a = line.split(None, 3)
        if len(a) < 4: continue
        s, h = cells(a[3])
        if s.startswith('000') or s.startswith('00') and not s.startswith('000'):
            pass
        # K event: head cell, then exactly '00' then '1'
        body = s[1:]
        if body.startswith('001'):
            got = decode(body); break
    n += 1
    if got != exp: bad += 1; print('MISS', l, 'exp', exp, 'got', got, p.stdout[-200:] if got is None else '')
print('F89 independent rule checks', n, 'bad', bad)
