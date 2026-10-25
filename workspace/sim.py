"""Accelerated Turing machine simulator for busy beaver hunting.

Tape is run-length encoded; "chain steps" consume an entire run of equal
symbols in one operation when the machine moves through them without
changing state, so regular counter-like machines reach astronomical step
counts in few operations.

Standard text format: states A..H, symbols 0/1, e.g.
  1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA   (BB(5) champion)
Each state contributes two entries (on read 0, on read 1); entry = write,
direction, next state; Z means halt and --- means an undefined transition.

Tape representation: two stacks of [symbol, count] runs. The head sits on
the top cell of the `right` stack; `left` top is the cell immediately to
the head's left. Blank (0) tape extends infinitely past both stacks.
"""

HALT = -1


def parse(tm: str):
    table = []
    for chunk in tm.strip().split("_"):
        entries = []
        for i in (0, 3):
            e = chunk[i:i + 3]
            if e == "---":
                entries.append(None)
                continue
            w = int(e[0])
            d = 1 if e[1] == "R" else -1
            ns = HALT if e[2] == "Z" else ord(e[2]) - 65
            entries.append((w, d, ns))
        table.append(entries)
    return table


def fmt(table):
    out = []
    for entries in table:
        s = ""
        for e in entries:
            if e is None:
                s += "---"
            else:
                w, d, ns = e
                s += f"{w}{'R' if d > 0 else 'L'}{'Z' if ns == HALT else chr(65 + ns)}"
        out.append(s)
    return "_".join(out)


def _push(stack, sym, n):
    if n <= 0:
        return
    if stack and stack[-1][0] == sym:
        stack[-1][1] += n
    else:
        stack.append([sym, n])


def _pop1(stack):
    """Remove one cell from the top run; return its symbol (0 if empty)."""
    if not stack:
        return 0
    sym = stack[-1][0]
    if stack[-1][1] == 1:
        stack.pop()
    else:
        stack[-1][1] -= 1
    return sym


def _ones(left, right):
    return sum(c for s, c in left if s == 1) + sum(c for s, c in right if s == 1)


def simulate(table, max_ops=100_000, max_steps=None):
    """Returns (status, steps, ones, ops); status in
    'halt', 'infinite', 'ops', 'steps', 'undef'."""
    left, right = [], []
    state = 0
    steps = 0
    ops = 0

    while ops < max_ops:
        ops += 1
        cur = right[-1][0] if right else 0
        entry = table[state][cur]
        if entry is None:
            return "undef", steps, _ones(left, right), ops
        w, d, ns = entry

        if ns == state:
            if d > 0:
                if not right:
                    if cur == 0:  # chains right over blank tape forever
                        return "infinite", steps, _ones(left, right), ops
                else:
                    # consume the whole run under/right of the head
                    n = right.pop()[1]
                    _push(left, w, n)
                    steps += n
                    if max_steps is not None and steps > max_steps:
                        return "steps", steps, _ones(left, right), ops
                    continue
            else:
                if not left and cur == 0:
                    # head writes and walks left into blank tape forever
                    return "infinite", steps, _ones(left, right), ops
                if left and left[-1][0] == cur:
                    # head cell + the n-cell run to the left all read `cur`:
                    # write w on each, end on the first cell past the run
                    _pop1(right)
                    n = left.pop()[1]
                    _push(right, w, n + 1)
                    _push(right, _pop1(left), 1)
                    steps += n + 1
                    if max_steps is not None and steps > max_steps:
                        return "steps", steps, _ones(left, right), ops
                    continue

        # single step
        if d > 0:
            _pop1(right)
            _push(left, w, 1)
        else:
            _pop1(right)
            _push(right, w, 1)
            _push(right, _pop1(left), 1)
        steps += 1
        state = ns
        if ns == HALT:
            return "halt", steps, _ones(left, right), ops
        if max_steps is not None and steps > max_steps:
            return "steps", steps, _ones(left, right), ops

    return "ops", steps, _ones(left, right), ops


if __name__ == "__main__":
    KNOWN = [
        ("1RB1LB_1LA1RZ", 6, 4),                                   # BB(2)
        ("1RB1RZ_1LB0RC_1LC1LA", 21, 5),                           # BB(3)
        ("1RB1LB_1LA0LC_1RZ1LD_1RD0RA", 107, 13),                  # BB(4)
        ("1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA", 47_176_870, 4098),  # BB(5)
    ]
    for tm, want_steps, want_ones in KNOWN:
        st, steps, ones, ops = simulate(parse(tm), max_ops=50_000_000)
        ok = st == "halt" and steps == want_steps and ones == want_ones
        print(f"{tm}: {st} steps={steps} ones={ones} ops={ops} "
              f"{'OK' if ok else 'MISMATCH want ' + str((want_steps, want_ones))}")
