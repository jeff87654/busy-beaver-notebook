"""Concrete 2-symbol Turing machines in the bbchallenge text format.

A transition is a tuple ``(write, direction, next_state)``.  Directions are
``+1`` for right and ``-1`` for left.  ``HALT`` is the distinguished halting
next-state.  A transition table is ``table[state][read_symbol]`` and may
contain ``None`` for a synthesis variable that has not been assigned yet.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

HALT = -1
Transition = tuple[int, int, int]
Table = list[list[Transition | None]]


def parse(text: str) -> Table:
    """Parse a standard ``1RB---_...`` machine string."""
    table: Table = []
    for chunk in text.strip().split("_"):
        if len(chunk) != 6:
            raise ValueError(f"state chunk must contain two transitions: {chunk!r}")
        entries: list[Transition | None] = []
        for start in (0, 3):
            entry = chunk[start : start + 3]
            if entry == "---":
                entries.append(None)
                continue
            if entry[0] not in "01" or entry[1] not in "LR":
                raise ValueError(f"bad transition: {entry!r}")
            if entry[2] == "Z":
                next_state = HALT
            elif "A" <= entry[2] <= "Z":
                next_state = ord(entry[2]) - 65
            else:
                raise ValueError(f"bad next state: {entry!r}")
            entries.append((int(entry[0]), 1 if entry[1] == "R" else -1, next_state))
        table.append(entries)
    return table


def format_table(table: Table) -> str:
    """Return the standard text representation of a transition table."""
    states: list[str] = []
    for entries in table:
        text = ""
        for entry in entries:
            if entry is None:
                text += "---"
            else:
                write, direction, next_state = entry
                if next_state == HALT:
                    label = "Z"
                elif 0 <= next_state < 26:
                    label = chr(65 + next_state)
                else:
                    raise ValueError(f"next state out of text range: {next_state}")
                text += f"{write}{'R' if direction > 0 else 'L'}{label}"
        states.append(text)
    return "_".join(states)


def empty_table(n_states: int) -> Table:
    return [[None, None] for _ in range(n_states)]


def copy_table(table: Table) -> Table:
    return [row[:] for row in table]


def complete_table(table: Table, filler: Transition = (1, 1, HALT)) -> Table:
    """Fill unused transitions arbitrarily so a candidate is a total TM."""
    return [[entry if entry is not None else filler for entry in row] for row in table]


@dataclass
class Config:
    """A concrete configuration.

    Only 1-cells are stored.  This keeps finite configurations canonical up
    to the infinitely many blank cells on both sides.
    """

    ones: set[int] = field(default_factory=set)
    head: int = 0
    state: int = 0

    @classmethod
    def from_cells(
        cls,
        cells: Iterable[int],
        *,
        head: int = 0,
        state: int = 0,
        origin: int = 0,
    ) -> "Config":
        ones = {origin + index for index, symbol in enumerate(cells) if symbol == 1}
        return cls(ones=ones, head=origin + head, state=state)

    @classmethod
    def from_string(
        cls, cells: str, *, head: int = 0, state: int = 0, origin: int = 0
    ) -> "Config":
        if set(cells) - {"0", "1"}:
            raise ValueError("cells string may only contain 0 and 1")
        return cls.from_cells(
            (int(ch) for ch in cells), head=head, state=state, origin=origin
        )

    def copy(self) -> "Config":
        return Config(set(self.ones), self.head, self.state)

    def read(self) -> int:
        return 1 if self.head in self.ones else 0

    def relative_ones(self) -> frozenset[int]:
        """Positions of 1s relative to the head."""
        return frozenset(position - self.head for position in self.ones)

    def canonical_key(self) -> tuple[int, frozenset[int]]:
        """Translation-invariant key used for exact loop detection."""
        return (self.state, self.relative_ones())

    def span(self) -> int:
        points = self.ones | {self.head}
        return max(points) - min(points) + 1

    def render(self, pad: int = 1) -> str:
        points = self.ones | {self.head}
        low, high = min(points) - pad, max(points) + pad
        cells = []
        for pos in range(low, high + 1):
            ch = "1" if pos in self.ones else "0"
            cells.append(f"[{ch}]" if pos == self.head else ch)
        state = "Z" if self.state == HALT else chr(65 + self.state)
        return f"{state}: {''.join(cells)}"


@dataclass
class RunOutcome:
    status: str  # checkpoint, halt, undef, timeout, loop, overflow
    config: Config
    steps: int
    undef: tuple[int, int] | None = None

    @property
    def ok_terminal(self) -> bool:
        return self.status in {"checkpoint", "halt"}


def run_until(
    table: Table,
    start: Config,
    *,
    checkpoint_state: int | None = None,
    max_steps: int = 1_000,
    max_span: int = 120,
    checkpoint_test=None,
) -> RunOutcome:
    """Run literally until a checkpoint state is re-entered or a bound hits.

    A checkpoint is recognized only after at least one transition, so a test
    can start in the checkpoint state.  If ``checkpoint_test`` is given, a
    return to the checkpoint state only counts when the test accepts the
    configuration (for example, the tape parses in the checkpoint form);
    other returns are passed through.  A repeated translation-invariant
    configuration is a genuine loop: Turing-machine dynamics commute with
    tape translation, and all cells outside ``Config.ones`` are blank.
    """
    cfg = start.copy()
    if cfg.state == HALT:
        return RunOutcome("halt", cfg, 0)
    seen = {cfg.canonical_key()}
    steps = 0
    while steps < max_steps:
        symbol = cfg.read()
        if not (0 <= cfg.state < len(table)):
            raise ValueError(f"state {cfg.state} is outside the table")
        entry = table[cfg.state][symbol]
        if entry is None:
            return RunOutcome("undef", cfg, steps, undef=(cfg.state, symbol))
        write, direction, next_state = entry
        if write:
            cfg.ones.add(cfg.head)
        else:
            cfg.ones.discard(cfg.head)
        cfg.head += direction
        cfg.state = next_state
        steps += 1
        if next_state == HALT:
            return RunOutcome("halt", cfg, steps)
        if checkpoint_state is not None and next_state == checkpoint_state:
            if checkpoint_test is None or checkpoint_test(cfg):
                return RunOutcome("checkpoint", cfg, steps)
        if cfg.span() > max_span:
            return RunOutcome("overflow", cfg, steps)
        key = cfg.canonical_key()
        if key in seen:
            return RunOutcome("loop", cfg, steps)
        seen.add(key)
    return RunOutcome("timeout", cfg, steps)


def run_from_blank(
    table: Table, *, max_steps: int = 1_000_000, max_span: int = 1_000_000
) -> RunOutcome:
    return run_until(
        table, Config(), checkpoint_state=None, max_steps=max_steps, max_span=max_span
    )
