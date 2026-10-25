"""Generate all 1- and 2-transition neighbors of a machine that can still halt (at least one undefined transition).

  python neighbors.py PARENT > neighbors.txt
Each transition slot may take any of the 32 defined values (write 0/1, move L/R, next state A-H) or be
undefined (---). Exact duplicates are removed here; equivalence up to relabeling / start swap is checked
later (dedup.py) only for the few survivors, since canonicalizing ~125k machines in Python is too slow.
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import dedup  # noqa: E402

LET = 'ABCDEFGH'


def slots(m):
    return [t for row in m.split('_') for t in (row[:3], row[3:])]


def join(ts):
    return '_'.join(ts[i] + ts[i + 1] for i in range(0, len(ts), 2))


def main():
    parent = sys.argv[1]
    base = slots(parent)
    n = len(base) // 2
    values = [f'{w}{d}{q}' for w in '01' for d in 'LR' for q in LET[:n]] + ['---']
    seen, out = set(), []

    def emit(ts):
        if '---' not in ts:
            return
        m = join(ts)
        if m in seen:
            return
        seen.add(m)
        out.append(m)

    for i in range(len(base)):
        for v in values:
            if v != base[i]:
                ts = list(base); ts[i] = v; emit(ts)
    for i, j in itertools.combinations(range(len(base)), 2):
        for v in values:
            if v == base[i]:
                continue
            for u in values:
                if u == base[j]:
                    continue
                ts = list(base); ts[i] = v; ts[j] = u; emit(ts)
    sys.stdout.write('\n'.join(out) + '\n')
    sys.stderr.write(f'{len(out)} neighbors with a halting transition\n')


if __name__ == '__main__':
    main()
