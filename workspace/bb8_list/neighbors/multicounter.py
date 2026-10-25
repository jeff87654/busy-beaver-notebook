"""Prototype of an encoding-agnostic "many counters" signal on tape snapshots (for champion-style digit lists).

  python multicounter.py SNAPS.tsv [SNAPS.tsv ...]      (stage1.exe snapshot dumps: machine, state, word)

A digit-list machine keeps many counters on the tape at once: runs u^n of one short unit u with large, varying
exponents, separated by short literals. The BB(7) champion writes each digit as (01)^(3d+1) between single 1s;
the 1RB1RA family writes 1^d between single 0s. Exponential and doubling counters keep only a few such runs.
For each snapshot and each unit u, the word is cut greedily (from the right) into runs of u and literal gaps;
a "counter block" is a run with exponent >= 3 bordered by gaps of at most 3 cells. The score of a machine is
the largest number of counter blocks in one snapshot, over units, together with the number of distinct exponents.
"""
import re
import sys
from collections import defaultdict

UNITS = ['1', '01', '10', '001', '011', '100', '110', '0001', '0011', '0111', '1000', '1100', '1110']


def blocks(word, u):
    """Counter blocks of unit u: exponents of maximal u-runs with exponent >= 3 whose gaps are <= 3 cells."""
    out, i, n, gap = [], 0, len(word), 0
    best = []
    pat = re.compile('(?:%s){3,}' % re.escape(u))
    pos = 0
    runs = []
    for m in pat.finditer(word):
        runs.append((m.start(), m.end(), (m.end() - m.start()) // len(u)))
    # chain runs whose gaps are short
    chain, prev_end = [], None
    for s, e, k in runs:
        if prev_end is not None and s - prev_end > 3:
            if len(chain) > len(best):
                best = chain
            chain = []
        chain.append(k)
        prev_end = e
    if len(chain) > len(best):
        best = chain
    return best


def score(words):
    top = (0, 0, '', [])
    for w in words:
        for u in UNITS:
            b = blocks(w, u)
            cand = (len(b), len(set(b)), u, b)
            if cand[:2] > top[:2]:
                top = cand
    return top


def main():
    snaps = defaultdict(list)
    for path in sys.argv[1:]:
        for l in open(path):
            f = l.rstrip('\n').split('\t')
            if len(f) == 3:
                snaps[f[0]].append(f[2])
    res = sorted(((score(ws), m) for m, ws in snaps.items()), reverse=True)
    hist = defaultdict(int)
    for (nb, nd, u, b), m in res:
        hist[min(nb, 12)] += 1
    print('machines by max counter blocks in one snapshot:', dict(sorted(hist.items())))
    for (nb, nd, u, b), m in res[:25]:
        print(f'{nb:3d} blocks, {nd:2d} distinct, unit {u:5s} {m}  {b[:16]}')


if __name__ == '__main__':
    main()
