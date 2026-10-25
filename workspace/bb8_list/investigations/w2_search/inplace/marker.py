"""marker.py M [M..]: marker survival.  Start = MARK + 0^gap + far_17 + [0 1^329|1|19] (std); follow S stages and
report the outcome, RSIGs, and the leftmost visited cell relative to the far region's left end (>= 0: the marker
and the gap were never visited, so they survive unchanged)."""
import sys, threading
from ilib import stage, rsig, far_of, word_of, SUF
MARKS = [('1', 1), ('11', 2), ('101', 3), ('1101', 1), ('10101', 2), ('111', 4)]
def run(M, mk, gap, S=200):
    pre = mk + '0' * gap
    word = pre + far_of(17) + word_of([0] + [1] * 329 + [1, 19]) + SUF
    A = -len(pre); lo = 10**9; mw = 10**9; rs = []
    for st in range(S):
        kind, d = stage(M, word, 10**9)
        if d.get('LO') is not None: lo = min(lo, A + d['LO'])
        if d.get('MW') is not None and d['MW'] < 10**17: mw = min(mw, A + d['MW'])
        if kind != 'K': return f'{kind}{d.get("slot","")}@{st}', rs, (lo, mw)
        r = rsig(d['toks'])
        if r and st > 0 and (not rs or st - rs[-1][0] > 3): rs.append((st, r[1]))
        if len(rs) >= 3: return 'RS3', rs, (lo, mw)
        A += d['shift']; word = d['newword']
    return 'MAX', rs, (lo, mw)
def go():
    for M in sys.argv[1:]:
        print(M)
        for mk, gap in MARKS:
            out, rs, lo = run(M, mk, gap)
            print(f'   marker {mk}+0^{gap}: {out} RS={rs} (word-start min, min changed cell) rel. far = {lo}', flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
