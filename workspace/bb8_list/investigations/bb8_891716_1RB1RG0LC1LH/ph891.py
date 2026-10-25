import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
M = "1RB1RG_0LC1LH_1LD1RC_---0LE_0RF0LA_0RA1LH_1RA0RC_1RA1LF"
pl.set_tm(M)
S = [1, 1]
A = (0, 1)        # tape '10' reversed (stream order, nearest the head first)
def Arun(v, c=0): return mkrun(A, {v: 1} if v else {}, c)
def Srun(v, c=0): return mkrun(tuple(S), {v: 1} if v else {}, c)
def cfg(L, R=None): return ('C', L, [BLANK] if R is None else R, '>')

PH = {}
# R1: S A^b S A^(a+1) T  ->  S A^(b+2) S A^a T
def r1(T):
    return (cfg(S + Arun('b') + S + [0, 1] + Arun('a') + T), cfg(S + Arun('b', 2) + S + Arun('a') + T))
# R23: S A^b S^(kc) A^(y+1) T  ->  S^(kc) A^(b+2) S A^y T      (kc = k+2 >= 2)
def r23(T, kc):
    return (cfg(S + Arun('b') + Srun('k', kc) + [0, 1] + Arun('y') + T),
            cfg(Srun('k', kc) + Arun('b', 2) + S + Arun('y') + T))
PH['R1v'] = r1([V('l')])
for kc in (2, 3, 4, 5, 6):
    PH['R23c%d' % kc] = r23([1, V('l')], kc)
    PH['R23e%d' % kc] = r23([BLANK], kc)


# Conv: S A^b S^(n+1) 1 BLANK -> S^(n+2) A S^b BLANK
PH['Conv'] = (cfg(S + Arun('b') + Srun('n', 1) + [1, BLANK]), cfg(Srun('n', 2) + [0, 1] + Srun('b') + [BLANK]))
PH['Conv3'] = (cfg(S + Arun('b') + Srun('n', 3) + [1, BLANK]), cfg(Srun('n', 4) + [0, 1] + Srun('b') + [BLANK]))
# Final: S A^b S^(m+1) BLANK -> S^(m+1) A^(b+2) 1 BLANK
PH['Fin'] = (cfg(S + Arun('b') + Srun('m', 1) + [BLANK]), cfg(Srun('m', 1) + Arun('b', 2) + [1, BLANK]))
PH['Fin3'] = (cfg(S + Arun('b') + Srun('m', 3) + [BLANK]), cfg(Srun('m', 3) + Arun('b', 2) + [1, BLANK]))


# ---- R23 (nested): ENTRY / LOOP phases.  Left stream at the loop head: L(j) = 1111 (11)^k (01)^j 010111 (01)^y T
def R23L(j, T):
    return [1, 1, 1, 1] + Srun('k') + Arun(j) + [0, 1, 0, 1, 1, 1] + Arun('y') + T
RB = mkrun((1, 0), {'b': 1}) + [BLANK]
PH['R23v2'] = r23([V('l')], 2)
for tag, T in (('o', [1, V('l')]), ('e', [BLANK]), ('v', [V('l')])):
    s0, _ = PH['R23c2'] if tag == 'o' else (PH['R23e2'] if tag == 'e' else PH['R23v2'])
    PH['ENT_R23' + tag] = (s0, ('C', R23L(None, T), RB, '>'))
    PH['LOOP_R23' + tag] = (('C', R23L('j', T), [1, 0] + RB, '>'),
                            ('C', [1, 1, 1, 1] + Srun('k') + Arun('j', 1) + [0, 1, 0, 1, 1, 1] + Arun('y') + T, RB, '>'))

def main():
    for w in sys.argv[1:] or list(PH):
        s, t = PH[w]
        try:
            r = drive(w, s, t, matchers=(), maxev=400, verbose=True)
        except Exception as e:
            print('  ERROR', type(e).__name__, e)
if __name__ == '__main__':
    main()
