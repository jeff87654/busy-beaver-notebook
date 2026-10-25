"""val3.py MACHINE 'k,p,c,z;..' [stages] [policy]: crafted round-2 start of the J0=1LK 2R+5 family:
[2^(k-4) 1 5 p 2 5 1^c 0^3 3 1^z | 1 | R] (R = 19 std / 2539 big).  Reports: counter-exhaustion stage (first K with
'4 0' after the 5), restarts, end (halt slot/stage)."""
import sys, threading
from t1lib import run, start_word, rsig
M = sys.argv[1]; combos = [tuple(int(x) for x in s.split(',')) for s in sys.argv[2].split(';')]
S = int(sys.argv[3]) if len(sys.argv) > 3 else 200; pol = sys.argv[4] if len(sys.argv) > 4 else 'std'
R0 = 2539 if pol == 'big' else 19
def go():
    for k, p, c, z in combos:
        rs = []; ev = {}
        def cb(st, kind, d):
            if kind == 'K':
                s = rsig(d[0][:-2])
                if s and not d[1] and s[1] >= 40 and st > 0: rs.append(f'c={s[1]}@{st}')
                if d[3] == 'left' and 'left' not in ev: ev['left'] = st
                if d[1] and 'far' not in ev: ev['far'] = st
        toks = [2] * (k - 4) + [1, 5, p, 2, 5] + [1] * c + [0, 0, 0, 3] + [1] * z + [1, R0]
        kind, st, d, v = run(M, start_word(toks), S, cb=cb, policy=pol, maxs=4 * 10**9)
        print(f'k={k} p={p} c={c} z={z}: {kind}@{st} {d[:2] if kind == "H" else ""} far@{ev.get("far")} left@{ev.get("left")} restarts={rs[:3]}', flush=True)
threading.stack_size(200 * 1024 * 1024); sys.setrecursionlimit(400000)
t = threading.Thread(target=go); t.start(); t.join()
