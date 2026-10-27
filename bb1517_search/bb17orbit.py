"""Trace BB17's real blank-tape orbit at the boundary between the f_w engine and the H..Q layers.

At an engine start the tape is   1^3 B> 1^l1 0 1^l2 0 ... 0 0 1^c 0 1^d [0 1^e]
(plus a final 0 before the blank).  We decode (A_left, list, c, d) at every engine start.
"""
import sys

sys.path.insert(0, '/workspace/workspace/bb_champs_17_18')
from machines import BB17  # noqa: E402
from rsim import Sim  # noqa: E402

sys.setrecursionlimit(10000)


def is_engine_start(s):
    return (s.st == 'B' and s.face == 'R' and len(s.L) > 1
            and s.L[0] == [1, 3] and s.L[1][0] == 0)


def decode_right(s):
    """right-of-head runs; split at the first 0^2 gap: list | c | d | e..."""
    runs = list(reversed(s.R))
    blocks = []
    cur = 0
    for sym, cnt in runs:
        if sym == 1:
            if cur == 0:
                blocks.append(cnt)
        else:
            if cnt >= 2:
                blocks.append(('gap', cnt))
            cur = 0
    return runs, blocks


def decode_lr(s):
    return list(reversed(s.L)), list(reversed(s.R))


def fmt_runs(runs):
    return ' '.join(f"{sym}^{cnt}" for sym, cnt in runs)


def main(name='BB17', nmacro=4_000_000):
    import machines
    m = getattr(machines, name)
    s = Sim(m)
    ev = []
    for i in range(nmacro):
        if s.halted:
            print(f"{name}: HALT at macro {i}, steps {s.steps}")
            break
        s.step()
        if is_engine_start(s):
            L, R = decode_lr(s)
            ev.append((s.steps, L, R))
            if len(ev) > 40:
                ev.pop(0)
    print(f"{name}: macros {i}, steps {s.steps}, halted {s.halted}, engine starts {len(ev)} (last 40)")
    for steps, L, R in ev[-25:]:
        print(f"  @{steps:>14d} L={fmt_runs(L)} | R={fmt_runs(R)}")


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'BB17',
         int(sys.argv[2]) if len(sys.argv) > 2 else 4_000_000)
