"""classrun.py MACHINE c1,c2,.. [z]: follow a machine from a crafted round start [2 5 1^c 0^3 3 1^z|1|19] (any class)
through the round end and the eater: report the next restart (c, delta) / HALT slot / junk, and the slots first read
after the round end (stage of first J0 read)."""
import sys, threading
from t1lib import run, start_word, rsig, rle
from nfol import run_stage
M = sys.argv[1]; cs = [int(x) for x in sys.argv[2].split(',')]; z = int(sys.argv[3]) if len(sys.argv) > 3 else 41
SL = [f'{q}{s}' for q in 'ABCDEFGHIJKLMNOP' for s in (0, 1)]
def go():
    for c in cs:
        w = start_word([2, 5] + [1] * c + [0, 0, 0, 3] + [1] * z + [1, 19])
        info = {'first': {}, 'w': w}
        def cb(st, kind, d):
            out, u = run_stage(M, info['w'], len(info['w']), 'G', 10**8)
            for i in range(32):
                if u >> i & 1 and SL[i] not in info['first']: info['first'][SL[i]] = st
            if kind == 'K':
                info['w'] = d[2]
                s = rsig(d[0][:-2])
                if s and not d[1] and st > 3 and s[1] >= 40:
                    return f'RESTART c={s[1]} d={s[1]-79} c%14={s[1]%14} c%42={s[1]%42} P={s[0]} st={st}'
        kind, st, d, v = run(M, w, 200, cb=cb)
        j = info['first'].get('J0')
        late = {k: s for k, s in info['first'].items() if j is not None and s >= j}
        print(f'c={c} c%14={c%14}: {v or kind} st={st} {d[:2] if kind=="H" else ""} J0first={j} slots_from_J0={late}', flush=True)
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
