"""worlds_champ.py: small-world halting configs of the BB(6) champion from S1(len0,0,0,a,b) (Rst0 -> halt)."""
import sys; sys.path.insert(0, '.')
from tm import parse, run
from vchamp3 import S1
M = parse('1RB1RA_1RC1RZ_1LD0RF_1RA0LE_0LD1RC_1RA0RE')
def halt_cfg(L, R, q0='E', maxs=10**7):
    tape = L + R; r = run(M, tape, len(L) - 1, q0, maxs)
    st, t, T, p, q, lo, hi, off = r
    if st != 'HALT': return None
    lo = min(lo, p) - 2; hi = max(hi, p) + 2
    s = ''.join(str(T[i]) for i in range(lo, hi + 1))
    return t, s, p - lo, q, T[p]
if __name__ == '__main__':
    out = []
    for len0 in range(1, 7):
        for a in range(0, 15):
            for b in (0, 1, 3, 7, 15):
                L, R = S1(len0, 0, 0, a, b); h = halt_cfg(L, R)
                if h is None: print('nohalt', len0, a, b, file=sys.stderr); continue
                t, s, pos, q, c = h
                out.append(f"W c1_{len0}_{a}_{b} {s} {pos} {q}")
                if (len0, a, b) == (1, 0, 0) or (len0, a, b) == (3, 5, 7): print(len0, a, b, 'halts after', t, 'at', q + str(c), file=sys.stderr)
    open(sys.argv[1], 'w').write('\n'.join(out) + '\n'); print(len(out), 'worlds', file=sys.stderr)
