"""Write a human-auditable transcript of the symbolic proofs (every macro step)."""
import io, contextlib
from symsim import *
import symsim
buf = io.StringIO()
L0s = Lemma('L0*', '[A0] 0 (100)^{j} 1010 (110)^{k}', '[A0] 0 (100)^{j+2k} 1010', {'j': 0, 'k': 1}, walled=(False, True))
jobs = [
 ('L0', '000 [A0] 0 (100)^{j} 1010 (110)^{k+1}', '[A0] 0 (100)^{j+2} 1010 (110)^{k}', {'j':0,'k':0}, [], (True, True)),
 ('R1', '[A0] 0 (100)^{x} 1010 (100)^{j} 1010 (110)^{k+1}', '[A0] 0 (100)^{2x+3} 1010 (100)^{j+2} 1010 (110)^{k}', {'x':1,'j':0,'k':0}, [L0s], (False, True)),
 ('T1', '[A0] 0 (100)^{x} 1010 (100)^{j} 1010 10100', '[A0] 0 (100)^{2x+3} 1010 10 (100)^{j+1} 00100 10', {'x':1,'j':0}, [L0s], (False, True)),
 ('R2', '[A0] 0 (100)^{x} 1010 (100)^{j} 10 (100)^{m+1}', '[A0] 0 (100)^{2x+3} 1010 (100)^{j+2} 10 (100)^{m}', {'x':1,'j':0,'m':0}, [L0s], (False, True)),
 ('T2', '[A0] 0 (100)^{x} 1010 (100)^{j} 10 00100', '[A0] 0 (100)^{2x+3} 1010 1010 (110)^{j} 10100', {'x':1,'j':0}, [L0s], (False, True)),
]
with open('proof_transcript.txt', 'w') as f:
    f.write('Symbolic proof transcript for 1RB1LD_1RC0RF_0LA0RA_0LA0LE_1LA0LG_0LA---_1RD1LG\n')
    f.write('Notation: tokens left of [Sb] are left of the head; (u)^{e} = u repeated e times.\n')
    f.write('Walls: "|" means the tape beyond is unknown and is never read; no wall = blank tape.\n\n')
    for name, lhs, rhs, lb, lem, W in jobs:
        f.write(f'=== {name}: {"|" if W[0] else ""} {lhs} {"|" if W[1] else ""}  ->  {"|" if W[0] else ""} {rhs} {"|" if W[1] else ""}   for {lb}\n')
        symsim._cross_cache.clear()
        s = io.StringIO()
        with contextlib.redirect_stdout(s):
            lm, n = prove(name, lhs, rhs, lb, lem, walled=W, trace=True)
        f.write(s.getvalue())
        f.write(f'--- reached RHS after {n} macro steps. Crossings used (block, state, dir -> new block, steps per block):\n')
        for (blk, st, d), res in sorted(symsim._cross_cache.items()):
            if res is not None:
                f.write(f'    {STATES[st]} {"->" if d>0 else "<-"} {blk}  =>  {res[0]}  ({res[1]} steps)\n')
        f.write('\n')
print(open('proof_transcript.txt').read()[:3000])
