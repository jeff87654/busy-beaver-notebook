"""Pinned transition-table fragments used as synthesis sketches."""
from __future__ import annotations

from .tm import Table, empty_table


def successor_sketch(n_states: int) -> Table:
    """A separator-shifting successor step for offset-one blocks.

    With the head on the last cell of the ``n`` block, the pinned transitions
    implement ``d0 -> d0 - 1`` and ``n -> n + 1`` when ``d0 > 0``, returning
    to state A on the new last cell of ``n``.  The remaining blocks are not
    touched.

    When ``d0 = 0`` the machine reaches the deliberately unassigned C0
    transition on the separator to the right of the one-cell ``d0`` block.
    A larger counter's refill/halting subroutine starts there.  States F
    onward are entirely free for that subroutine.
    """
    if n_states < 5:
        raise ValueError("the split successor sketch needs at least five states")
    table = empty_table(n_states)
    table[0][1] = (1, 1, 1)   # A1 = 1RB: leave the n block
    table[1][0] = (0, 1, 1)   # B0 = 0RB: cross the separator
    table[1][1] = (1, 1, 2)   # B1 = 1RC: inspect d0's second cell
    table[2][1] = (1, -1, 3)  # C1 = 1LD: d0 > 0, scan back left
    table[3][0] = (1, 1, 4)   # D0 = 1RE: extend n into the separator
    table[3][1] = (1, -1, 3)  # D1 = 1LD: continue left
    table[4][1] = (0, -1, 0)  # E1 = 0LA: shorten d0, return to checkpoint
    return table
