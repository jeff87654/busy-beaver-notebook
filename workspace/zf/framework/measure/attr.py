"""Attribute Wade's 324 DAG cells to subsystems by deleting parts of the program and recounting.
Uses ext/turing_machine_explorer/zf2.py unchanged (imported)."""
import sys, io, contextlib
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\ext\turing_machine_explorer')
import zf2 as Z
ORDER=[16, 17, 3, 18, 4, 7, 8, 9, 11, 5, 12, 13, 14, 2, 15, 0, 1, 6, 10, 19]
def count(cls, order=ORDER):
    m=cls(); m.debug=False; m.AXIOMORDER=order; m.build_machine()
    st=set(s[0] for s in m.tm.states)
    fw=len([s for s in st if s[0].isdigit()]); return fw, len(st)-fw, len(st)
print('full', count(Z.ZF2))
# variant: no axioms at all (only DET, GEN kept) -> measures axiom template cost
class NoAx(Z.ZF2):
    def axioms(self):
        a=super().axioms(); return a[:2]
print('DET+GEN only (no axiom templates)', count(NoAx,[0,1]))
class OnlyAx(Z.ZF2):
    def axioms(self):
        a=super().axioms(); return a[2:]
print('axioms only, no DET/GEN', count(OnlyAx,[i-2 for i in ORDER if i>=2]))
class NoB6a(Z.ZF2):
    def axioms(self):
        a=super().axioms(); a[8]=[a[8][0]]+[]  # drop B6a entirely (replace with trivial)
        return a
print('no B6a', count(NoB6a))
class NoLogic(Z.ZF2):
    def axioms(self): return []
print('no axioms at all (parse + v_0 + check only)', count(NoLogic,[]))
