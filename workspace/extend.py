"""Validate the halt-extension construction on fully simulable champions.

Construction: find the champion's halt transition (w, d, Z), redirect it to
a fresh state H, and define H as a sweep: on 1 -> 1LH (or 1RH), on 0 ->
1RZ. The sweep provably terminates from any halting configuration because
the tape holds finitely many 1s, so the (n+1)-state machine halts after
strictly more steps than the n-state original — regardless of what the
final configuration looks like.

Validated here on BB(4) and BB(5), then applied to the BB(7) champion.
"""
from sim import parse, fmt, simulate, HALT


def extend(tm: str, sweep_dir: str = "L") -> str:
    table = parse(tm)
    n = len(table)
    halts = [(i, j) for i in range(n) for j in (0, 1)
             if table[i][j] is not None and table[i][j][2] == HALT]
    assert len(halts) == 1, f"expected exactly one halt transition, got {halts}"
    (i, j) = halts[0]
    w, d, _ = table[i][j]
    table[i][j] = (w, d, n)  # redirect halt into new state H
    sd = 1 if sweep_dir == "R" else -1
    # H: on 0 -> write 1, move opposite the sweep, halt; on 1 -> sweep on
    table.append([(1, -sd, HALT), (1, sd, n)])
    return fmt(table)


def report(name, tm, max_ops=50_000_000):
    st, steps, ones, ops = simulate(parse(tm), max_ops=max_ops)
    print(f"{name}: {st}  steps={steps}  ones={ones}  ops={ops}")
    return st, steps, ones


if __name__ == "__main__":
    for name, champ in [
        ("BB(4) champ", "1RB1LB_1LA0LC_1RZ1LD_1RD0RA"),
        ("BB(5) champ", "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA"),
    ]:
        _, s0, o0 = report(f"{name} original ", champ)
        for sd in ("L", "R"):
            ext = extend(champ, sd)
            st, s1, o1 = report(f"{name} +sweep{sd} ", ext)
            gain = s1 - s0
            ok = st == "halt" and s1 > s0 and o1 == o0 + 1
            print(f"   -> {ext}")
            print(f"   -> gain={gain} steps, ones {o0}->{o1}  "
                  f"{'CONSTRUCTION OK' if ok else 'UNEXPECTED'}")
        print()

    bb7 = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF"
    for sd in ("L", "R"):
        print(f"BB(7) champ + sweep{sd} (8 states): {extend(bb7, sd)}")
