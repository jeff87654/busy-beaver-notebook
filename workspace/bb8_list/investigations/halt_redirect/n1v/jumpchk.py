"""jumpchk.py: literal verification (ktrace2.exe) of every jump type of the n1 period at tiny depth, against
follow2.jump()'s predicted event configuration (exact small accumulators only)."""
from st import *
import subprocess, os
KT = r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/ktrace2.exe'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)


def kmoments(toks, maxsteps=400_000_000, maxlines=100000):
    word = mf35.word_of_tokens(toks) + '1010'
    r = subprocess.run([KT, N1, word, str(len(word)), 'G', 'G', str(maxsteps), str(maxlines), '100000'],
                       capture_output=True, text=True, creationflags=LOW)
    out = []
    for line in r.stdout.splitlines():
        if line.startswith(('HALT', 'END', 'TAPE')):
            out.append(line)
            continue
        step, _, body = line.partition(':')
        body, _, tail = body.partition('|')
        toks2 = []
        for t in body.split():
            if t == '...' or t.startswith('JUNK'):
                toks2 = None
                break
            if '*' in t:
                a, c = t.split('*')
                toks2 += [int(a)] * int(c)
            else:
                toks2.append(int(t))
        out.append((int(step), toks2, tail.strip()))
    return out


def predicted(toks):
    items, newp, info = dojump(toks)
    vals = {}
    for p, v in newp.items():
        if not v.exact:
            return None, info, newp
        vals[p] = v.x
    new = []
    for e in items:
        m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
        c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
        new += [m] * c
    return new, info, newp


cases = [
    ('J1 2R+3->2 n=0 u=1', "7 2 5 | 1 1"),
    ('J1 n=1 u=1', "7 2 5 1 | 1 1"),
    ('J1 u=2 n=0', "7 2 8 | 1 1"),
    ('J2 nonstd r=2 n=1', "2 2 5 1 0 0 45 1 | 1 2"),
    ('J2 nonstd r=2 n=1 big token', "2 2 5 1 0 0 5085 1 | 1 2"),
    ('J3 clear 2R2+5 n=0', "2 2 5 1 0 0 42 0 7 | 1 1"),
    ('J3 n=1 token 4', "2 2 5 1 0 0 42 0 4 1 | 1 1"),
    ('J4 2R3+3->2 n=0', "2 2 5 1 0 0 5 | 1 1"),
    ('J5 nonstd r=2 n=1', "2 2 5 1 0 0 0 1 43 1 | 1 2"),
    ('J6 clear 2R5+5 n=0', "2 2 5 1 0 0 0 1 40 0 7 | 1 1"),
    ('Jx exhaustion token 6 n=0', "6 | 1 1"),
    ('Jx token 6 n=1', "6 1 | 1 1"),
    ('Jx token 9 n=0', "9 | 1 1"),
    ('Jy 0 4 n=1', "0 4 1 | 1 1"),
    ('Jy 0 7 n=0', "0 7 | 1 1"),
    ('J0 transient token 9 n=0', "2 5 1 0 0 0 9 | 1 1"),
    ('J1t token 7 at 0^4 n=0', "2 5 1 0 0 0 0 7 | 1 1"),
    ('J2t token 5 n=0', "2 5 1 0 0 5 | 1 1"),
]
for name, s in cases:
    lhs, rhs = s.split('|')
    toks = expand(lhs) + [int(x) for x in rhs.split()]
    pred, info, newp = predicted(toks)
    if pred is None:
        print(f"{name}: prediction not exact ({newp}) - skipped")
        continue
    km = kmoments(toks)
    found = [x for x in km if isinstance(x, tuple) and x[1] == pred]
    nk = len([x for x in km if isinstance(x, tuple)])
    res = ('FOUND at step ' + str(found[0][0])) if found else 'NOT FOUND'
    print(f"{name}: pred={rle(pred)} ev={info.get('event')} -> {res} ({nk} K-moments, last={km[-1] if km else None})")
