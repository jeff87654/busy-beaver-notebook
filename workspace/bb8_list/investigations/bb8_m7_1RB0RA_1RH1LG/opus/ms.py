"""Milestones of the used-up transient (13 tokens D(1), r = 3b+2) and mexp exploration between them."""
import sys, time, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gen'))
from common import *
from shapes import *
import mexp
from mexp import show

def to_stream(segs):
    """segments left to right: '0101' literal or ('R', block, var) or ('R', block, {var: k})."""
    out = []
    for seg in reversed(segs):
        if isinstance(seg, str):
            out += [int(ch) for ch in reversed(seg)]
        else:
            _, block, var = seg
            cnt = var if isinstance(var, dict) else {var: 1}
            out.append(run(tuple(int(ch) for ch in reversed(block)), **cnt))
    return out

def cfgB(segs):
    """head in B on the blank right of the word, blank left of the word."""
    return ('B', to_stream(segs) + [BLANK], [BLANK], '>')

TAIL = '111001'
M0 = cfgB(['101' * 13, '1010', ('R', '101010', 'b'), TAIL])
M1 = cfgB(['101' * 13, '1', '1010', ('R', '101010101010', 'b'), '0', TAIL])
M2 = cfgB(['10' * 4, ('R', '101010101010', 'b'), '0', '111', '001' * 14])
M3 = cfgB(['1010', '111', ('R', '001' * 12, 'b'), '001' * 8, '1' * 39, '001001'])
M4 = cfgB(['1010', '111', ('R', '001' * 12, 'b'), '001' * 7, '0', '1111', '000111' * 5, '00110', '111111', '001001'])
Y0 = cfgB(['101' * 13, ('R', '101010', 'b'), '11', '01', '00', TAIL])
MS = {'Y0': Y0, 'M0': M0, 'M1': M1, 'M2': M2, 'M3': M3, 'M4': M4}

if __name__ == '__main__':
    a, b = sys.argv[1], sys.argv[2]
    splits = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    pl.LEMMAS.clear()
    t0 = time.time()
    try:
        tree = mexp.explore(MS[a], MS[b], splits=splits)
        print(a, '->', b, 'OK %.1fs' % (time.time() - t0))
        if '-v' in sys.argv:
            print('\n'.join(mexp.describe(tree))[:6000])
    except Exception as e:
        print(a, '->', b, 'FAILED %.1fs' % (time.time() - t0), str(e)[:1500])
