"""Probe BB17's layer structure with a third counter e on the tape.

Tape layout at a layer entry (BB17 convention):
    left  : 1^A (01)^p 0        head in state H, facing right
    right : 0 1^c 0 1^d [0 1^e] 0
Right side as run list in tape order: [(0,1),(1,c),(0,1),(1,d),(0,1),(1,e),(0,1)]

Goal: find out what BB17's w+2 layer (L,M,N,O,P,Q) does when a 4th counter block e
sits to the right of d.
"""
import sys

sys.path.insert(0, '/workspace/workspace/bb_champs_17_18')
from machines import BB17, parse  # noqa: E402
from rsim import Sim  # noqa: E402


def table(s):
    T = parse(s)
    for st in sorted({k[0] for k in T}):
        row = []
        for b in (0, 1):
            t = T.get((st, b))
            row.append('---' if t is None else f"{t[0]}{t[1]}{t[2]}")
        print(f"  {st}: {row[0]:>4} {row[1]:>4}")


def mk(mstr, left_runs, right_runs, st='B', face='R'):
    """left_runs/right_runs in tape order (leftmost first / rightmost last)."""
    s = Sim(mstr)
    for sym, cnt in left_runs:
        Sim.push(s.L, sym, cnt)
    for sym, cnt in reversed(right_runs):
        Sim.push(s.R, sym, cnt)
    s.st = st
    s.face = face
    return s


def is_engine_start(s):
    return (s.st == 'B' and s.face == 'R' and len(s.L) > 1
            and s.L[0] == [1, 3] and s.L[1][0] == 0)


def craft(A, p, c, d, e=None):
    left = [(1, A)] + [(0, 1), (1, 1)] * p + [(0, 1)]
    right = [(0, 1), (1, c), (0, 1), (1, d)]
    if e is not None:
        right += [(0, 1), (1, e)]
    right += [(0, 1)]
    return left, right


def run_to_engine(mstr, A, p, c, d, e=None, maxsteps=300000):
    left, right = craft(A, p, c, d, e)
    s = mk(mstr, left, right, st='H', face='R')
    while True:
        if s.halted:
            return ('HALT', s.steps, s)
        if s.steps > maxsteps:
            return ('TIME', s.steps, s)
        s.step()
        if s.steps > 0 and is_engine_start(s):
            return ('OK', s.steps, s)


def read_right(s):
    out = list(reversed(s.R))
    while out and out[-1][0] == 0:
        out.pop()
    return out


def show(tag, res):
    kind, steps, s = res
    lr = ' '.join(f"{sym}^{cnt}" for sym, cnt in read_right(s))
    left = ' '.join(f"{sym}^{cnt}" for sym, cnt in reversed(s.L))
    print(f"{tag}: {kind:4} steps={steps:7d} | L={left} | R={lr}  [{s.st}{'R' if s.face == 'R' else 'L'}]")


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'BB17'
    import machines
    m = getattr(machines, name)
    print(f"{name} transition table:")
    table(m)
    print()
    for c in (0, 1, 3):
        for d in (0, 1, 2, 3):
            for e in (None, 1, 2, 4):
                tag = f"A=3 p=1 c={c} d={d} e={e}"
                try:
                    show(tag, run_to_engine(m, 3, 1, c, d, e))
                except Exception as ex:
                    print(f"{tag}: EXC {type(ex).__name__} {ex}")
