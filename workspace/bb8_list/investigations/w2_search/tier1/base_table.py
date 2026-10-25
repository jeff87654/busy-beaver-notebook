"""base_table.py: n1 itself (J0 undefined) from a round start [2 5 1^c 0^3 3 1^z | 1 | 19] for a range of counters c:
does the round reach J0 (eater entry), with which far k, or junk?  usage: python base_table.py C0 C1 [z] [policy]"""
import sys, threading
from t1lib import N1, run, start_word, fark, rsig
c0, c1 = int(sys.argv[1]), int(sys.argv[2]); z = int(sys.argv[3]) if len(sys.argv) > 3 else 32
pol = sys.argv[4] if len(sys.argv) > 4 else 'std'
def go():
    for c in range(c0, c1 + 1):
        last = {}
        def cb(st, kind, d):
            if kind == 'K':
                last['toks'] = d[0]; last['far'] = d[1]; last['st'] = st
                if st > 3 and rsig(d[0][:-2]) and not d[1]:
                    return 'RESTART c=%d' % rsig(d[0][:-2])[1]
        S = 40 + 6 * c // 14 * 2
        kind, st, d, v = run(N1, start_word([2, 5] + [1] * c + [0, 0, 0, 3] + [1] * z + [1, 19]), S, policy=pol, cb=cb)
        k, rest = fark(last.get('far', ''))
        from t1lib import rle
        tk = rle(last['toks'][:-2])[:60] if 'toks' in last else ''
        print(f'c={c} c%14={c % 14} c%42={c % 42}: {kind if v is None else v} st={st} {d[:2] if kind == "H" else ""} '
              f'lastK st={last.get("st")} k={k} rest={rest[:30]} toks={tk}', flush=True)
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
