"""remnant.py: n1 from a no-far left-event config with a stray bit pattern left of the list:
PATTERN + 0^g + word([7 1^N | 1 | 19]).  Which restart counter (delta) follows?  Output remnant.tsv"""
import sys, threading, itertools
from t1lib import N1, run, word_of, rsig
N = 329
def go():
    for L in range(1, 7):
        for bits in itertools.product('01', repeat=L - 1):
            pat = '1' + ''.join(bits)
            for g in range(1, 7):
                w = pat + '0' * g + word_of([7] + [1] * N + [1, 19]) + '1010'
                def cb(st, kind, d):
                    if kind == 'K':
                        s = rsig(d[0][:-2])
                        if s and not d[1] and s[1] >= 40: return s
                kind, st, d, v = run(N1, w, 30, cb=cb)
                out = f'RESTART\tc={v[1]}\td={v[1]-79}\tP={v[0]}' if v else f'{kind}\t{d[:2] if kind == "H" else ""}'
                print(f'{pat}\tg={g}\t{out}\tst={st}', flush=True)
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
