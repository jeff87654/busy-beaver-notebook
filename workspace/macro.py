"""Marxen-style macro-machine simulator: treat k tape cells as one block
symbol, memoize how the base machine traverses a block, and chain-step over
runs of identical blocks. Exact step counts; sound 'infinite' verdicts.

Representation: two RLE stacks of [block, count]; the head sits between
them. facing=+1 means the head is about to enter the top block of `right`
at its leftmost cell; facing=-1 enters the top of `left` at its rightmost
cell. Blank (all-zero) blocks extend past both stacks.
"""
from sim import HALT


def _inner(table, k, state, block, entry, bound):
    """Run the base machine inside one k-cell block.
    entry: 0 = enter at cell 0 (from left), 1 = enter at cell k-1.
    Returns ('exit', new_state, exit_side, new_block, steps)
         or ('halt', new_block, steps)
         or ('loop',) | ('undef',)
    exit_side: -1 left, +1 right."""
    cells = list(block)
    pos = 0 if entry == 0 else k - 1
    st = state
    steps = 0
    while steps <= bound:
        e = table[st][cells[pos]]
        if e is None:
            return ("undef",)
        w, d, ns = e
        cells[pos] = w
        steps += 1
        pos += d
        st = ns
        if st == HALT:
            return ("halt", tuple(cells), steps)
        if pos < 0:
            return ("exit", st, -1, tuple(cells), steps)
        if pos >= k:
            return ("exit", st, 1, tuple(cells), steps)
    return ("loop",)  # (pos, state, contents) must have repeated: pigeonhole


def _push(stack, blk, n):
    if n <= 0:
        return
    if stack and stack[-1][0] == blk:
        stack[-1][1] += n
    else:
        stack.append([blk, n])


def _ones(left, right):
    return (sum(c * sum(b) for b, c in left)
            + sum(c * sum(b) for b, c in right))


def simulate_macro(table, k=4, max_ops=200_000):
    """Returns (status, steps, ones, ops); status in
    'halt', 'infinite', 'ops', 'undef'."""
    ZERO = (0,) * k
    nstates = len(table)
    bound = nstates * k * (2 ** k) + 1
    memo = {}
    left, right = [], []
    state = 0
    facing = 1
    steps = 0
    ops = 0

    while ops < max_ops:
        ops += 1
        if facing > 0:
            stack, other = right, left
            entry = 0
        else:
            stack, other = left, right
            entry = 1
        blank = not stack
        blk = stack[-1][0] if stack else ZERO

        key = (state, blk, entry)
        res = memo.get(key)
        if res is None:
            res = _inner(table, k, state, blk, entry, bound)
            memo[key] = res

        tag = res[0]
        if tag == "loop":
            return "infinite", steps, _ones(left, right), ops
        if tag == "undef":
            return "undef", steps, _ones(left, right), ops
        if tag == "halt":
            _, nblk, s = res
            steps += s
            if stack:
                if stack[-1][1] == 1:
                    stack.pop()
                else:
                    stack[-1][1] -= 1
            _push(stack, nblk, 1)
            return "halt", steps, _ones(left, right), ops

        _, nstate, exit_side, nblk, s = res
        if blank and exit_side == facing:
            # traversing virgin blank tape and continuing the same way
            if nstate == state:
                return "infinite", steps, _ones(left, right), ops
            steps += s
            _push(other, nblk, 1)
            state = nstate
            continue

        if not blank and exit_side == facing and nstate == state:
            # chain: the whole run of identical blocks gets traversed
            n = stack.pop()[1]
            _push(other, nblk, n)
            steps += s * n
            continue

        # single block
        if stack:
            if stack[-1][1] == 1:
                stack.pop()
            else:
                stack[-1][1] -= 1
        if exit_side == facing:
            _push(other, nblk, 1)
        else:
            _push(stack, nblk, 1)
            facing = -facing
        steps += s
        state = nstate

    return "ops", steps, _ones(left, right), ops


def best_macro(table, ks=(2, 3, 4, 5, 6, 8), max_ops=200_000):
    """Try several block sizes; return first conclusive verdict."""
    last = None
    for k in ks:
        st, steps, ones, ops = simulate_macro(table, k, max_ops)
        last = (st, steps, ones, ops, k)
        if st in ("halt", "infinite", "undef"):
            return last
    return last


if __name__ == "__main__":
    import math
    import time
    from sim import parse

    TESTS = [
        ("BB(4) champ", "1RB1LB_1LA0LC_1RZ1LD_1RD0RA", 107, 13),
        ("BB(5) champ", "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA", 47_176_870, 4098),
        ("BB(6) 10^36534", "1RB1LE_1RC1RF_1LD0RB_1RE0LC_1LA0RD_1RZ1RC", None, None),
    ]
    for name, tm, ws, wo in TESTS:
        table = parse(tm)
        for k in (2, 3, 4, 6, 8):
            t0 = time.time()
            st, steps, ones, ops = simulate_macro(table, k, max_ops=2_000_000)
            dt = time.time() - t0
            mag = f"10^{math.log10(steps):.1f}" if steps > 10**9 else str(steps)
            flag = ""
            if ws is not None and st == "halt":
                flag = "OK" if (steps == ws and ones == wo) else "MISMATCH"
            print(f"{name} k={k}: {st} steps={mag} ones~{ones if ones < 10**6 else f'10^{math.log10(ones):.1f}'} ops={ops} {dt:.1f}s {flag}")
            if st == "halt":
                break
