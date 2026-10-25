"""val2.py MACHINE 'c,z,R;c,z,R;..' [stages] [policy]: crafted round start [2 5 1^c 0^3 3 1^z | 1 | R] (no far):
follow through the round end + eater; report restarts and the halt (stage, slot)."""
import sys, threading
from t1lib import run, start_word, rsig
M = sys.argv[1]; combos = [tuple(int(x) for x in s.split(',')) for s in sys.argv[2].split(';')]
S = int(sys.argv[3]) if len(sys.argv) > 3 else 400; pol = sys.argv[4] if len(sys.argv) > 4 else 'std'
def go():
    for c, z, R in combos:
        rs = []; ev = {}
        def cb(st, kind, d):
            if kind == 'K':
                s = rsig(d[0][:-2])
                if s and not d[1] and s[1] >= 40 and st > 3: rs.append(f'c={s[1]}@{st}')
                if d[1] and 'far' not in ev: ev['far'] = st
        kind, st, d, v = run(M, start_word([2, 5] + [1] * c + [0, 0, 0, 3] + [1] * z + [1, R]), S, cb=cb, policy=pol, maxs=int(float(sys.argv[5])) if len(sys.argv) > 5 else 2 * 10**9)
        print(f'c={c} z={z} R={R}: {kind} st={st} {d[:2] if kind == "H" else ""} first-far@{ev.get("far")} restarts={rs}', flush=True)
threading.stack_size(200 * 1024 * 1024); sys.setrecursionlimit(400000)
t = threading.Thread(target=go); t.start(); t.join()
