"""Machine-level stage specs (start, target, positive) for the explorer."""
import sys, time
from common import *
import mexp
Zb = (1, 0, 1)
def zeros(**v):
    return [run(Zb, **v)]
def tokp(k, **var):
    """token D(k + 2*var-form): 1 (01)^k (0101)^var"""
    return [1] + [0, 1] * k + ([run((0, 1, 0, 1), **var)] if var else [])
CT = [1, 0, 1, 0, 1, 0, 1, 0, 1, run((0, 1), c=1), V('l')]      # the C token D(c+4), then l
def W2(wv, Rv, Zv, extra_zeros=9, pre_w=0, pre_R=0, beyond=None, zblk=1, rtail=None):
    Rrun = [run((1, 0, 1, 0), **Rv)] if Rv else []
    left = [1, 0, 0, 1, 1, 0, 1, 1, 1] + [0, 1, 1, 1, 0, 1, 1, 1] * pre_w + ([run((0, 1, 1, 1, 0, 1, 1, 1), **wv)] if wv else []) + (beyond if beyond is not None else CT)
    right = [1, 0, 1, 0] * pre_R + Rrun + [0, 1, 0, 1] + [1, 0, 1] * extra_zeros + ([run((1, 0, 1) * zblk, **Zv)] if Zv else []) + (rtail or [BLANK])
    return ('D', left, right, '>')
def Wgen(wv, right, pre_w=0, beyond=None):
    """W-form with an explicit right side (list of planner tokens, ending in a terminator)"""
    left = [1, 0, 0, 1, 1, 0, 1, 1, 1] + [0, 1, 1, 1, 0, 1, 1, 1] * pre_w + ([run((0, 1, 1, 1, 0, 1, 1, 1), **wv)] if wv else []) + (beyond if beyond is not None else [1, V('l')])
    return ('D', left, list(right), '>')
JUNK = [1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1]
def K(near_list, a, r, tail=None):
    """near_list: tokens nearest-first (each a left stream list), a, r: token streams; head G right of tail D2"""
    return G((tail or tok(2)) + r + a + sum(near_list, []))
PARTS = {
  # S3: F [C, 2, 0, 2] 0^Z | 1 | R  ->  F [C-4, 2R+6, 7] 0^(Z+1) | 1 | 1
  'S3': (K([zeros(Z=1), tok(2), tok(0), tok(2), tok(4, c=1), [V('l')]], tok(1), tok(0, R=1)),
         K([zeros(Z=1), tok(1), tok(7), tok2(6, R=1), tok(0, c=1), [V('l')]], tok(1), tok(1)), ()),
  # S4: F [C, 2] 0^Z | 1 | R  ->  F [C-3, 2R+6] 0^Z | 1 | 2
  'S4': (K([zeros(Z=1), tok(2), tok(3, c=1), [V('l')]], tok(1), tok(0, R=1)),
         K([zeros(Z=1), tok2(6, R=1), tok(0, c=1), [V('l')]], tok(1), tok(2)), ()),
  # S2: F [C, x, 0] 0^Z | 1 | R  ->  F [C-4, 2, 0, 2R+4-(x-3)/2] 0^(Z+x-2) | 1 | 1   with x = 2y+3, R = y+s
  'S2': (K([zeros(Z=1), tok(0), tok(3, y=2), tok(4, c=1), [V('l')]], tok(1), tok(0, y=1, s=1)),
         K([zeros(Z=1, y=2), tok(1), tok(4, y=1, s=2), tok(0), tok(2), tok(0, c=1), [V('l')]], tok(1), tok(1)), ('s', 'y', 'c', 'Z')),
  'S2free': (K([zeros(Z=1), tok(0), tokp(3, y=1), tok(4, c=1), [V('l')]], tok(1), tok(0, R=1)), None, ('y', 'c', 'Z', 'R')),
  # refill: D6^N D3 [0, x, 0] 0^Z | 1 | R -> D6^(N-1) D0 D2 D0 [2R-(x+1)/2, 2, 0, 5] 0^(Z+x+7) | 1 | 1
  'REFfree': (K([zeros(Z=1), tok(0), tokp(3, y=1), tok(0), tok(3), [run(tuple(tok(6)), n=1)], tok(6), [BLANK]], tok(1), tok(0, R=1)), None, ('y', 'Z', 'R')),
  # halt: F2 [1, 2, 0, 2] 0^Z | 1 | R with F2 = D6^N D0 D2 D0
  'HALT': (K([zeros(Z=1), tok(2), tok(0), tok(2), tok(1), tok(0), tok(2), tok(0), tok(6), tok(6), [V('l')]], tok(1), tok(0, R=1)), None, ('Z', 'R')),
  # stage 1: [D6^(N+1), D2, D2, D0, D2, 0^Z | 1 | R] -> [D6^N, D3, D(2R+5), D8, 0^(Z+2) | 1 | 2]
  'ST1': (K([zeros(Z=1), tok(2), tok(0), tok(2), tok(2), [run(tuple(tok(6)), n=1)], tok(6), [BLANK]], tok(1), tok(0, R=1)),
          K([zeros(Z=1), tok(1), tok(1), tok(8), tok2(5, R=1), tok(3), [run(tuple(tok(6)), n=1)], [BLANK]], tok(1), tok(2)), ('Z', 'R')),
  # S2 with x = 2y+3, y = 2w+5 (x = 4w+13): first part, R free
  'S2a': (K([zeros(Z=1), tok(0), [1] + [0, 1] * 13 + [run((0, 1) * 4, w=1)], tok(4, c=1), [V('l')]], tok(1), tok(0, R=1)), None, ('w', 'c', 'Z', 'R')),
  # S2 waypoint W(w, R, Z): l (10)^c 1 0 1 0 1 0 1 0 1 (11101110)^w 1 1 1 0 1 1 0 0 1 D> (1010)^R 0 1 0 1 (101)^9 (101)^Z
  'S2A': (K([zeros(Z=1), tok(0), [1] + [0, 1] * 13 + [run((0, 1) * 4, w=1)], [1, V('l')]], tok(1), tok(0, R=1)),
           W2(dict(w=1), dict(R=1), dict(Z=1), beyond=[1, V('l')]), ('w', 'Z', 'R')),
  'S2R': (W2(dict(w=1), dict(R=1), dict(Z=1), pre_w=1, pre_R=1, beyond=[1, V('l')]), W2(dict(w=1), dict(R=1), dict(Z=1), extra_zeros=13, beyond=[1, V('l')]), ()),
  'REFfree2': (W2(None, dict(t=1), dict(Z=1), pre_R=1, beyond=[1] + tok(3) + [run(tuple(tok(6)), n=1)] + tok(6) + [BLANK]), None, ('t', 'n', 'Z')),
  # refill tail: W(0, t+4, Z) on [C=0, D3, D6, D6, l] -> [l, D6, D0, D2, D0, 2t+1, 2, 0, 5] 0^(Z+20) | 1 | 1
  'REFc': (W2(None, dict(t=1), dict(Z=1), pre_R=4, beyond=[1] + tok(3) + tok(6) + tok(6) + [V('l')]),
           K([zeros(Z=1), tok(1) * 20, tok(5), tok(0), tok(2), tok(1, t=2), tok(0), tok(2), tok(0), tok(6), [V('l')]], tok(1), tok(1)), ('t', 'Z')),
  # S2 with x = 5: F [C, 5, 0] 0^Z | R -> F [C-4, 2, 0, 2R+3] 0^(Z+3)
  'S2x5': (K([zeros(Z=1), tok(0), tok(5), tok(4, c=1), [V('l')]], tok(1), tok(0, R=1)),
           K([zeros(Z=1), tok(1) * 3, tok2(3, R=1), tok(0), tok(2), tok(0, c=1), [V('l')]], tok(1), tok(1)), ('Z', 'R')),
  # stage 0: K(0^(M+1); 0; b) of the BB(8) record (r-token R = 3b+1), blank beyond
  'ST0free': (K([zeros(M=1), tok(1), [BLANK]], tok(1), [1, 0, 1, run((0, 1) * 3, b=1)]), None, ('M', 'b')),
  # S2 halting branch: the R-run is used up while the x-stack is not
  'S2H0': (W2(dict(w=1), None, dict(Z=1), pre_w=1, beyond=[1, V('l')]), None, ('Z',)),
  'S2H5': (W2(dict(w=1), None, dict(k=1), pre_w=1, beyond=[1, V('l')], extra_zeros=12, zblk=5), None, ('k',)),
  'S2Rv': (W2(dict(w=1), dict(R=1), dict(Z=1), pre_w=1, pre_R=1, beyond=[1, V('l')], rtail=[V('r')]), W2(dict(w=1), dict(R=1), dict(Z=1), extra_zeros=13, beyond=[1, V('l')], rtail=[V('r')]), ()),
  'S2Rv0': (W2(dict(w=1), dict(R=1), None, pre_w=1, pre_R=1, beyond=[1, V('l')], rtail=[V('r')]), W2(dict(w=1), dict(R=1), None, extra_zeros=13, beyond=[1, V('l')], rtail=[V('r')]), ()),
  # refill for n = 10k+17 zeros: W(w+2, 0, n) -> W(w, units 6k+13, zeros 6k+11, junk tail)
  'H1': (W2(dict(w=1), None, dict(k=1), pre_w=2, extra_zeros=17, zblk=10, beyond=[1, V('l')]),
         Wgen(dict(w=1), [1, 0] * 13 + [run((1, 0) * 6, k=1), 0, 1, 0, 1] + [1, 0, 1] * 11 + [run((1, 0, 1) * 6, k=1)] + JUNK + [BLANK]), ('k', 'w')),
  # odd W-round: units 2R+3 -> 2R+1, zeros +4, any tail r
  'WRodd': (Wgen(dict(w=1), [1, 0, 1, 0, run((1, 0, 1, 0), R=1), 1, 0, 0, 1, 0, 1] + [1, 0, 1] * 9 + [V('r')], pre_w=1),
            Wgen(dict(w=1), [run((1, 0, 1, 0), R=1), 1, 0, 0, 1, 0, 1] + [1, 0, 1] * 13 + [V('r')]), ()),
  # last unit: W(w+P, units 1, zeros z, junk) -> HALT
  'H2free': (Wgen(dict(w=1), [1, 0, 0, 1, 0, 1] + [1, 0, 1] * 9 + [run((1, 0, 1), z=1)] + JUNK + [BLANK], pre_w=2), None, ('z',)),
  'S2a1': (K([zeros(Z=1), tok(0), [1] + [0, 1] * 13 + [run((0, 1) * 4, w=1)], tok(4, c=1), [V('l')]], tok(1), tok(0, R=1)),
           W2(dict(w=1), dict(R=1), dict(Z=1)), ('w', 'c', 'Z', 'R')),
  # one round of the W-loop: W(w+1, R+1, Z) -> W(w, R, Z+4)
  'S2r': (W2(dict(w=1), dict(R=1), dict(Z=1), pre_w=1, pre_R=1), W2(dict(w=1), dict(R=1), dict(Z=1), extra_zeros=13), ()),
  # tail: W(0, t+1, Z) -> F [C-4, 2, 0, 2t+1] 0^(Z+11) | 1 | 1
  'S2c': (W2(None, dict(t=1), dict(Z=1), pre_R=1),
          K([zeros(Z=1), tok(1) * 11, tok(1, t=2), tok(0), tok(2), tok(0, c=1), [V('l')]], tok(1), tok(1)), ('t', 'c', 'Z')),
}
if __name__ == '__main__':
    for name in sys.argv[1].split(','):
        s, t, pos = PARTS[name]
        print(name, pl.show(s)); print('   ->', pl.show(t) if t else 'HALT')
        t0 = time.time()
        try:
            tree = mexp.explore(s, t, positive=frozenset(pos))
            print('  OK (%.1fs)' % (time.time() - t0))
            if '-v' in sys.argv: print('\n'.join(mexp.describe(tree)))
        except Exception as e:
            print('  FAIL', str(e)[:1500])
