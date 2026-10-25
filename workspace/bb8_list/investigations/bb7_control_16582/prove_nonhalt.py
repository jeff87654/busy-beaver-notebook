"""Symbolic proof that 1RB1LD_1RC0RF_0LA0RA_0LA0LE_1LA0LG_0LA---_1RD1LG never halts.

Configurations (tape blank beyond both ends, head on the leftmost used cell):
  beta (x,j,k,t) = [A0] 0 (100)^x 1010 (100)^j 1010 (110)^k 10100 (10)^t 1101
  gamma(x,j,m,t) = [A0] 0 (100)^x 1010 (100)^j 10   (100)^m 00100 (10)^t 1101
Rules (proved below with symbolic parameters; the part of the tape right of
the '|' wall is never read, so (10)^t 1101 is untouched):
  L0 : 000 [A0] 0 (100)^j 1010 (110)^(k+1) |  ->  [A0] 0 (100)^(j+2) 1010 (110)^k |
  L0*: [A0] 0 (100)^j 1010 (110)^k |          ->  [A0] 0 (100)^(j+2k) 1010 |     (induction on k, blank left)
  R1 : beta (x,j,k+1,t) -> beta (2x+3, j+2, k,   t)
  T1 : beta (x,j,0,  t) -> gamma(2x+3, 0,   j+1, t+1)
  R2 : gamma(x,j,m+1,t) -> gamma(2x+3, j+2, m,   t)
  T2 : gamma(x,j,0,  t) -> beta (2x+3, 0,   j,   t)
"""
import json, sys
from symsim import *

out = {}

def show(name, lemma, n, lb):
    print(f"PROVED {name}: {lemma.lhs_str}  ->  {lemma.rhs_str}   (lower bounds {lb}, {n} macro steps)")
    out[name] = {'lhs': lemma.lhs_str, 'rhs': lemma.rhs_str, 'lower_bounds': lb, 'macro_steps': n,
                 'walls': list(lemma.walled)}

# L0: one bounce, walls on both sides (touches nothing outside the pattern)
lb = {'j': 0, 'k': 0}
L0, n = prove('L0', '000 [A0] 0 (100)^{j} 1010 (110)^{k+1}', '[A0] 0 (100)^{j+2} 1010 (110)^{k}', lb)
show('L0', L0, n, lb)

# L0*: by induction on k from L0 (L0 holds for all j>=0, k>=0; each use needs
# three blank cells left of the head, supplied by the blank left tape).
L0s = Lemma('L0*', '[A0] 0 (100)^{j} 1010 (110)^{k}', '[A0] 0 (100)^{j+2k} 1010',
            {'j': 0, 'k': 1}, walled=(False, True))
out['L0*'] = {'lhs': L0s.lhs_str, 'rhs': L0s.rhs_str, 'lower_bounds': {'j': 0, 'k': 1},
              'justification': 'induction on k using L0; left side blank', 'walls': [False, True]}
print('DERIVED L0* by induction from L0')

W = (False, True)   # blank to the left, wall on the right (right context untouched)
lb = {'x': 1, 'j': 0, 'k': 0}
R1, n = prove('R1', '[A0] 0 (100)^{x} 1010 (100)^{j} 1010 (110)^{k+1}',
              '[A0] 0 (100)^{2x+3} 1010 (100)^{j+2} 1010 (110)^{k}', lb, [L0s], walled=W)
show('R1', R1, n, lb)

lb = {'x': 1, 'j': 0}
T1, n = prove('T1', '[A0] 0 (100)^{x} 1010 (100)^{j} 1010 10100',
              '[A0] 0 (100)^{2x+3} 1010 10 (100)^{j+1} 00100 10', lb, [L0s], walled=W)
show('T1', T1, n, lb)

lb = {'x': 1, 'j': 0, 'm': 0}
R2, n = prove('R2', '[A0] 0 (100)^{x} 1010 (100)^{j} 10 (100)^{m+1}',
              '[A0] 0 (100)^{2x+3} 1010 (100)^{j+2} 10 (100)^{m}', lb, [L0s], walled=W)
show('R2', R2, n, lb)

lb = {'x': 1, 'j': 0}
T2, n = prove('T2', '[A0] 0 (100)^{x} 1010 (100)^{j} 10 00100',
              '[A0] 0 (100)^{2x+3} 1010 1010 (110)^{j} 10100', lb, [L0s], walled=W)
show('T2', T2, n, lb)

# Also try the weakest bounds (x>=0) to report what is actually needed.
for name, lhs, rhs, lb0 in [
    ('R1', '[A0] 0 (100)^{x} 1010 (100)^{j} 1010 (110)^{k+1}', '[A0] 0 (100)^{2x+3} 1010 (100)^{j+2} 1010 (110)^{k}', {'x': 0, 'j': 0, 'k': 0}),
    ('T1', '[A0] 0 (100)^{x} 1010 (100)^{j} 1010 10100', '[A0] 0 (100)^{2x+3} 1010 10 (100)^{j+1} 00100 10', {'x': 0, 'j': 0}),
    ('R2', '[A0] 0 (100)^{x} 1010 (100)^{j} 10 (100)^{m+1}', '[A0] 0 (100)^{2x+3} 1010 (100)^{j+2} 10 (100)^{m}', {'x': 0, 'j': 0, 'm': 0}),
    ('T2', '[A0] 0 (100)^{x} 1010 (100)^{j} 10 00100', '[A0] 0 (100)^{2x+3} 1010 1010 (110)^{j} 10100', {'x': 0, 'j': 0})]:
    try:
        prove(name, lhs, rhs, lb0, [L0s], walled=W)
        print(f'  {name} also holds with x>=0')
    except ProofFail as e:
        print(f'  {name} with x>=0: not proved by this tool ({str(e)[:80]}...)')

json.dump(out, open('proof_rules.json', 'w'), indent=1)
print('wrote proof_rules.json')
