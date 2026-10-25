"""resume.py MACHINE 'TOKENS (rle, digits.. a r)' STAGES LOG: continue a follower run from a J-output token list (no far),
with a deep recursion limit; logs K-moments, restarts, halts."""
import sys, threading
from t1lib import stage, start_word, rsig, rle
from nfol import expand
M, toks, S, logf = sys.argv[1], expand(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
POL = sys.argv[5] if len(sys.argv) > 5 else "std"; MAXS = int(float(sys.argv[6])) if len(sys.argv) > 6 else 4 * 10**8; BIGK = int(sys.argv[7]) if len(sys.argv) > 7 else 1
def go():
    lf = open(logf, 'w'); word = start_word(toks)
    for st in range(S):
        kind, d = stage(M, word, MAXS, POL, BIGK)
        if kind != 'K':
            lf.write(f'{st} {kind} {d}\n'); lf.flush(); print(st, kind, d, flush=True); return
        t, far, new, ev, nz, newl = d
        s = rsig(t[:-2])
        tag = f' RESTART c={s[1]}' if (s and not far and s[1] >= 40) else ''
        lf.write(f'{st} K: {rle(t[:-2])[:150]} | far={len(far)} ev={ev} zeros={nz}{tag}\n'); lf.flush()
        if tag: print(st, tag, flush=True)
        word = new
    print('MAX', flush=True)
threading.stack_size(200 * 1024 * 1024); sys.setrecursionlimit(1000000)
t = threading.Thread(target=go); t.start(); t.join()
