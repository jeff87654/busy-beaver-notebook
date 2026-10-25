"""Extract the clause word lists straight from zf2.py by stubbing its subroutines (no hand transcription).
Run from ext/turing_machine_explorer:  python ../../tools/extract_clauses.py
Prints each clause as a sequence of tokens and compares the RPN part with gen_enum.AXIOMS."""
import sys, os
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import zf2
from gen_enum import AXIOMS, INDEX

class Sym(zf2.ZF2):
    pass

WORDS = ['v_0', 'v_1', 'v_2', 'v_3', 'par1', 'par2', 'par3', 'weq', 'wel', 'wim', 'wn', 'wal', 'wex', 'wa', 'select']
for w in WORDS:
    setattr(Sym, w, (lambda w: lambda self: w)(w))
Sym.cparam = lambda self, p: ('cparam', str(p))
Sym.while_decnz = lambda self, var, body: ('while_decnz', str(var), body)
Sym.if_eq = lambda self, a, b, body: ('if_eq', str(a), str(b), body)
Sym.debug_assert_eq_val = lambda self, a, v: ()

s = Sym()
clauses = s.axioms()
assert len(clauses) == len(INDEX)
ok = True
for i, (name, cl) in enumerate(zip(INDEX, clauses)):
    rpn = [t for t in cl if isinstance(t, str) and t != 'select']
    other = [t for t in cl if not isinstance(t, str)]
    mine = AXIOMS[name].split()
    same = rpn == mine
    ok &= same
    print(f'{i:2d} {name:4s} {"OK " if same else "DIFF"} rpn={" ".join(rpn)}')
    if other:
        print('      other:', other)
    if not same:
        print('      gen_enum:', ' '.join(mine))
print('ALL MATCH' if ok else 'MISMATCHES')
print('AXIOMORDER from README/zf2.py optimizer must be checked separately; zf2.tm is the source of truth.')
