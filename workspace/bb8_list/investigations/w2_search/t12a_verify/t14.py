"""t14.py M WORDFILE r-list: replace the accumulator token of a stage input word and run literally to the first RSIG."""
import lsimpy, sys
M = sys.argv[1]; w = open(sys.argv[2]).read().strip()
far, t = lsimpy.parse_k(w[:-1])
print('base', len(far), lsimpy.rle(t)[:80])
from sweep_util import rng
for r in rng(sys.argv[3]):
    ww = far + lsimpy.word_of(t[:-1] + [r]) + '1010'
    x = lsimpy.run(M, ww, kmode=-2, maxs=4 * 10**10)
    if x['res'] != 'K': print(r, x['line'][:80]); continue
    toks = x['toks']; s = lsimpy.rle(toks[:-2])
    print(r, x['steps'], 'far', len(x['far']), x['far'] == far[:len(x['far'])] and len(x['far']), s[:70], 'a,r=', toks[-2:], flush=True)
