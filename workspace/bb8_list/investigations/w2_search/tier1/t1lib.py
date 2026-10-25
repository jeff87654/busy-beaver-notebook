"""t1lib.py: shared helpers for the tier1 (route 3) residue scan. Imports n1's follower tools read-only."""
import sys, os
N1DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'n1')
sys.path.insert(0, os.path.abspath(N1DIR))
from fstep import stage                      # noqa: E402  (one follower stage: literal gstage + jump)
from sim import far_of, word_of, FAR_TAIL    # noqa: E402
from nfol import rle                         # noqa: E402
N1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
L12 = N1[:-6] + '0LK0LC_0LC1LL_0LK0RC'
S11 = N1[:-6] + '0LK0LC_0LC1LJ'

def fark(far):
    """number of leading '10101' blocks of a far string (the D2 run length k), and the rest"""
    k = 0
    while far.startswith('10101', 5 * k):
        k += 1
    return k, far[5 * k:]

def start_word(toks, far=''):
    return far + word_of(toks) + '1010'

def rsig(d):
    """round-start signature on K-moment digits: P 2 5 1^c 0^3 9 1^z  -> (P, c, z) or None"""
    z = 0
    while z < len(d) and d[len(d) - 1 - z] == 1: z += 1
    i = len(d) - 1 - z
    if i < 5 or d[i] != 9 or d[i-1] != 0 or d[i-2] != 0 or d[i-3] != 0: return None
    j = i - 4; c = 0
    while j >= 0 and d[j] == 1: c += 1; j -= 1
    if j < 1 or d[j] != 5 or d[j-1] != 2: return None
    return (tuple(d[:j-1]), c, z)

def run(M, word, stages, maxs=10**8, policy='std', cb=None):
    """follow; cb(st, kind, d) may return a value to stop.  returns (kind, st, last data, stopval)"""
    for st in range(stages):
        kind, d = stage(M, word, maxs, policy)
        if cb:
            v = cb(st, kind, d)
            if v is not None:
                return kind, st, d, v
        if kind != 'K':
            return kind, st, d, None
        word = d[2]
    return 'MAX', stages, None, None
