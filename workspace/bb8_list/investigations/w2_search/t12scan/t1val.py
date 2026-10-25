"""t1val.py FILE: Tier-1 validation of halting machines (one per line): std far_k + [0 1^n|1|19] for (k,n) in
(17,329) (29,329) (41,371) (17,2849) (17,41); real start std; big k = 17, 77 (n = 329, R-sized counters trimmed to
their class mod 42); prints outcome + RSIG list (stage:c) per test."""
import sys, threading
import ilib
from ilib import stage, rsig, far_of, word_of, SUF, real_start
def run(M, k, n, pol, real=False, S=200):
    if real: word, head, state = real_start(6)
    else: word, head, state = far_of(k) + word_of([0] + [1] * n + [1, 19]) + SUF, None, 'G'
    rs = []
    for st in range(S):
        kind, d = stage(M, word, 3 * 10**9, pol, ctrim=1 if pol == 'big' else 0, head=head, state=state); head, state = None, 'G'
        if kind != 'K': return f'{kind}{d.get("slot","")}@{st}', rs
        r = rsig(d['toks'])
        if r and st > 0 and (not rs or st - rs[-1][0] > 3): rs.append((st, r[1]))
        word = d['newword']
    return 'MAX', rs
def trim(new, ct):
    out = list(new); i = 0
    while i + 2 < len(out) - 2:
        if out[i] == 2 and out[i + 1] == 5:
            j = i + 2
            while j < len(out) - 2 and out[j] == 1: j += 1
            m = j - i - 2
            if m > 1000:
                m2 = m % 42; out = out[:i + 2] + [1] * m2 + out[j:]; j = i + 2 + m2
            i = j
        else: i += 1
    return out
ilib.trim_counter = trim
def go():
    for M in [l.strip() for l in open(sys.argv[1]) if l.strip()]:
        print(M, flush=True)
        tests = [(17, 329, 'std', False), (29, 329, 'std', False), (41, 371, 'std', False), (17, 2849, 'std', False), (17, 41, 'std', False),
                 (0, 0, 'std', True), (17, 329, 'big', False), (77, 329, 'big', False), (0, 0, 'big', True)]
        for k, n, pol, real in tests:
            out, rs = run(M, k, n, pol, real)
            tag = 'REAL' if real else f'k={k} n={n}'
            print(f'   {pol} {tag}: {out} RS={rs}', flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
