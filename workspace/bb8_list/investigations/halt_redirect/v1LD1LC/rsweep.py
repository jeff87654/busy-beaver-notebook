"""Residue sweeps: which values of the accumulator r (and of the parked tokens) give the stage templates?  Runs each
literal stage for consecutive small values and prints the set of residues (mod 2, 3, 4, 5, 8) of the matching values.
This tells which residue hypotheses a Coq lemma for each stage needs.  usage: python rsweep.py"""
import sys, json
from fractions import Fraction
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/v1LD1LC')
from lit1 import run, rle, fmt
from stages import PRE6

def classify(name, values, f):
    ok, no = [], []
    for v in values:
        try:
            r = f(v)
        except Exception as ex:
            r = 'EXC ' + repr(ex)[:40]
        (ok if r is True else no).append((v, r))
    print(f'{name}: match for {[v for v, _ in ok]}')
    print(f'   no match for {[(v, r if isinstance(r, str) else "") for v, r in no]}')
    for q in (2, 3, 4, 5, 8):
        print(f'   residues mod {q}: match {sorted(set(v % q for v, _ in ok))}, no-match {sorted(set(v % q for v, _ in no))}')

def same(o, exp, a, r):
    if o['kind'] == 'K' and o['toks'] == exp and o['a'] == a and o['r'] == r and not o['far']:
        return True
    return fmt(o)[:90]

z, u = 32, 2      # z == 2 mod 5 (the real class of S11); other stages are z-independent (quick grid)
# S1-type R3 step from D3 (any r expected)
classify('S1 r', range(1, 60), lambda r: same(run([9] * u + [8, 3] + [1] * z, 1, r), [9] * u + [8, 0, 2 * r + 5] + [1] * (z - 1), 1, 1))
classify('S2 r', range(1, 70), lambda r: same(run([9] * u + [8, 0] + [1] * z, 1, r), [9] * (u - 1) + [5, 3, 0, 3, 2 * r + 3] + [1] * (z + 2), 1, 2))
classify('S4 r (A=19)', range(1, 70), lambda r: same(run([9] * (u - 1) + [5, 3, 0, 3, 38, 0] + [1] * z, 1, r),
                                                    [9] * (u - 1) + [2, 7, 0, 0, 3, 3] + [0, 3] * 7 + [0, 2 * r + 3] + [1] * (z + 2), 1, 2))
classify('S4 A (r=19)', range(5, 70), lambda A: same(run([9] * (u - 1) + [5, 3, 0, 3, 2 * A, 0] + [1] * z, 1, 19),
                                                    [9] * (u - 1) + [2, 7, 0, 0, 3, 3] + [0, 3] * ((A - 5) // 2) + [0, 41] + [1] * (z + 2), 1, 2))
def s6(k, A, r):
    inp = [9] * (u - 1) + [2, 7, 0, 0, 3, 3] + [0, 3] * k + [0, 2 * A, 0] + [1] * z
    exp = ([9] * (u - 1) + [2, 7, 0, 0, 3, 3] + [0, 3] * (k - 2) + [0, 0, 5] + [1, 0] * (A - 11) + [0, 1, 1, 7, 1, 1, 0, 3, 3]
           + [0, 3] * ((r + 1) // 2) + [0, 7] + [1] * (z + 3))
    return same(run(inp, 1, r), exp, 1, 2)
classify('S6 r (k=7, A=19)', range(1, 70), lambda r: s6(7, 19, r))
classify('S6 A (k=7, r=19)', range(11, 70), lambda A: s6(7, A, 19))
classify('S6 k (A=19, r=19)', range(0, 12), lambda k: s6(k, 19, 19))
def s8(j, A, r):
    Q = PRE6(u, 5, A)
    return same(run(Q + [0, 3] * j + [0, 4, 0] + [1] * z, 1, r), Q + [0, 3] * (j - 3) + [0, 2, 1, 1, 2 * r + 5, 1, 1, 1, 1, 0, 0, 9] + [1] * (z - 3), 1, 1)
classify('S8 r (j=10)', range(1, 70), lambda r: s8(10, 19, r))
classify('S8 j (r=19)', range(0, 12), lambda j: s8(j, 19, 19))
def s10(P, r):
    Q = PRE6(u, 5, 19) + [0, 3] * 7 + [0, 2, 1, 1]
    return same(run(Q + [2 * P + 5, 1, 1, 1, 1, 0, 0, 0] + [1] * z, 1, r), Q + [2 * P + 5, 1, 0, 1, 2 * r + 3] + [1] * (z + 1), 1, 1)
classify('S10 r (P=19)', range(1, 70), lambda r: s10(19, r))
classify('S10 P (r=19)', range(1, 70), lambda P: s10(P, 19))
COEF = {k: [Fraction(x) for x in v] for k, v in json.load(open('ones_coef.json')).items()}
def s11(k, A, j, P, r):
    Q = PRE6(u, k, A) + [0, 3] * j + [0, 2, 1, 1]
    o = run(Q + [2 * P + 5, 1, 0, 1, 2] + [1] * z, 1, r)
    if o['kind'] != 'H' or o['state'] != 'I' or o['read'] != 0:
        return fmt(o)[:90]
    co = COEF[str(z % 5)]
    pred = co[0] + co[1] * u + co[2] * z + co[3] * k + co[4] * A + co[5] * j + co[6] * P + co[7] * r
    return True if pred == o['ones'] else f'halt I0 but ones {o["ones"]} != {pred}'
classify('S11 r (P=19)', range(1, 70), lambda r: s11(5, 19, 7, 19, r))
classify('S11 P (r=19)', range(1, 70), lambda P: s11(5, 19, 7, P, 19))
def s11z(zz):
    o = run(PRE6(u, 5, 19) + [0, 3] * 7 + [0, 2, 1, 1, 43, 1, 0, 1, 2] + [1] * zz, 1, 19)
    if o['kind'] != 'H' or o['state'] != 'I' or o['read'] != 0:
        return fmt(o)[:90]
    co = COEF[str(zz % 5)]
    pred = co[0] + co[1] * u + co[2] * zz + co[3] * 5 + co[4] * 19 + co[5] * 7 + co[6] * 19 + co[7] * 19
    return True if pred == o['ones'] else f'halt I0 but ones {o["ones"]} != {pred}'
classify('S11 z (P=r=19)', range(1, 45), s11z)
