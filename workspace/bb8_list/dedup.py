"""Detect candidates that are the same machine (up to behavior from the blank tape) as one already decided.

Equivalences used:
  - Relabeling. States are renamed in order of first visit when simulating from the blank tape, like
    tree normal form; states never visited keep their relative order at the end.
  - Start-state swap. If state X has the same 0-transition as A, then swapping the labels A <-> X gives a
    machine whose run from the blank tape is identical after step 1 (both starts take the same first step).
Two machines are treated as duplicates if some swap-variant of one has the same canonical form as some
swap-variant of the other.

  python dedup.py M1 [M2 ...]    # prints 'duplicate-of <known>' or 'new' per machine
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LET = 'ABCDEFGHIJKLMNOP'   # up to 16 states (the BB(9) champion is in the known list)


def parse(m):
    rows = m.split('_')
    t = {}
    for i, row in enumerate(rows):
        for s in (0, 1):
            x = row[3 * s:3 * s + 3]
            t[(LET[i], s)] = None if x == '---' or x[2] == 'Z' else (int(x[0]), x[1], x[2])
    return t, len(rows)


def fmt(t, n):
    out = []
    for i in range(n):
        row = ''
        for s in (0, 1):
            v = t[(LET[i], s)]
            row += '---' if v is None else f'{v[0]}{v[1]}{v[2]}'
        out.append(row)
    return '_'.join(out)


def relabel(t, n, perm):  # perm: old -> new
    return {(perm[q], s): (None if v is None else (v[0], v[1], perm[v[2]])) for (q, s), v in t.items()}


def canonical(m, steps=20000):
    t, n = parse(m)
    order, tape, pos, q = ['A'], {}, 0, 'A'
    for _ in range(steps):
        v = t[(q, tape.get(pos, 0))]
        if v is None:
            break
        tape[pos] = v[0]
        pos += 1 if v[1] == 'R' else -1
        q = v[2]
        if q not in order:
            order.append(q)
            if len(order) == n:
                break
    order += [x for x in LET[:n] if x not in order]
    return fmt(relabel(t, n, {old: LET[i] for i, old in enumerate(order)}), n)


def swap_variants(m):
    t, n = parse(m)
    out = [m]
    for x in LET[1:n]:
        if t[('A', 0)] is not None and t[('A', 0)] == t[(x, 0)]:
            perm = {q: q for q in LET[:n]}
            perm['A'], perm[x] = x, 'A'
            out.append(fmt(relabel(t, n, perm), n))
    return out


def keys(m):
    return {canonical(v) for v in swap_variants(m)}


def known_machines():
    ms = set()
    for l in (ROOT / 'proofs' / 'README.md').read_text(encoding='utf-8').splitlines():
        mm = re.match(r'\| `[^`]+\.v` \| `([^`]+)`', l)
        if mm:
            ms.add(mm.group(1))
    disp = ROOT / 'investigations' / 'dispatched.txt'
    if disp.exists():
        ms |= {l.split('\t')[0] for l in disp.read_text().splitlines() if l.strip()}
    pf = ROOT / 'prefilter_results.json'
    if pf.exists():
        import json
        ms |= {m for m, r in json.loads(pf.read_text()).items() if r['status'] == 'verified_nonhalting'}
    return ms


def index():
    idx = {}
    for m in known_machines():
        for k in keys(m):
            idx.setdefault(k, m)
    return idx


def check(ms):
    idx = index()
    res = {}
    for m in ms:
        hit = next((idx[k] for k in keys(m) if k in idx and idx[k] != m), None)
        res[m] = hit
    return res


if __name__ == '__main__':
    for m, hit in check(sys.argv[1:]).items():
        print(f'duplicate-of {hit}' if hit else 'new', m)
