"""Symbolic verification over repeated tape words such as ``(01)^n``.

The affine verifier in :mod:`.symbolic` handles variable-length runs of one
symbol.  Champion tapes also contain variable repetitions of short words.
This module therefore works at item boundaries: a tape is a list of items
``word^repeat`` with affine repeat counts, and the head sits at a boundary
facing the next item.  Traversing one word is a finite concrete simulation.
If every repetition would be traversed in the same state and exit through
the far side in that same state, the whole item is consumed as one shift
rule; otherwise one repetition is peeled off symbolically.

Verdicts have the same three-valued meaning as in :mod:`.symbolic`.  A
checkpoint here is specifically the right-edge form used by the champion
analyses: the checkpoint state, facing right, with only blank tape ahead.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from .symbolic import (
    Assumptions,
    BranchResult,
    Expr,
    SymbolicResult,
    _CounterexampleBranch,
    _UnknownBranch,
    _split_positive,
)
from .tm import HALT, Table


@dataclass(frozen=True)
class PItem:
    word: tuple[int, ...]
    repeats: Expr
    infinite: bool = False

    def substituted(self, assumptions: Assumptions) -> "PItem":
        return PItem(self.word, self.repeats.substitute(assumptions), self.infinite)


def cells(text: str) -> PItem:
    if not text or set(text) - {"0", "1"}:
        raise ValueError("a tape word must be a nonempty string of 0/1")
    return PItem(tuple(int(ch) for ch in text), Expr.constant(1))


def rep(text: str, repeats: Expr) -> PItem:
    if not text or set(text) - {"0", "1"}:
        raise ValueError("a tape word must be a nonempty string of 0/1")
    return PItem(tuple(int(ch) for ch in text), repeats)


def _psentinel() -> PItem:
    return PItem((0,), Expr.constant(0), infinite=True)


@dataclass
class PConfig:
    items: list[PItem]
    boundary: int  # index of the item to the right of the head
    facing: int  # +1 reads the right item's first cell; -1 the left's last
    state: int
    assumptions: Assumptions
    steps: Expr = Expr.constant(0)
    depth: int = 0
    visited: frozenset = frozenset()
    # Ancestor snapshots (state, boundary, facing, items, assumptions,
    # depth) for cycle detection, and signatures of failed accelerations.
    history: tuple = ()
    accel_tried: frozenset = frozenset()
    steps_known: bool = True

    def clone(self) -> "PConfig":
        return PConfig(
            list(self.items),
            self.boundary,
            self.facing,
            self.state,
            dict(self.assumptions),
            self.steps,
            self.depth,
            self.visited,
            self.history,
            self.accel_tried,
            self.steps_known,
        )

    def snapshot(self) -> tuple:
        return (
            self.state,
            self.boundary,
            self.facing,
            tuple(self.items),
            tuple(sorted(self.assumptions.items())),
            self.depth,
        )

    def canonical_key(self):
        items = tuple(
            (item.word, item.repeats.substitute(self.assumptions), item.infinite)
            for item in self.items
        )
        return (
            self.state,
            self.boundary,
            self.facing,
            items,
            tuple(sorted(self.assumptions.items())),
        )

    def render(self) -> str:
        parts: list[str] = []
        for index, item in enumerate(self.items):
            if index == self.boundary:
                arrow = ">" if self.facing > 0 else "<"
                state = "Z" if self.state == HALT else chr(65 + self.state)
                parts.append(f"|{state}{arrow}|")
            if item.infinite:
                parts.append("0^inf")
            else:
                word = "".join(str(cell) for cell in item.word)
                repeats = item.repeats.substitute(self.assumptions)
                parts.append(word if repeats == Expr.constant(1) else f"({word})^({repeats})")
        if self.boundary >= len(self.items):
            parts.append("|")
        return " ".join(parts)


def _pnorm(config: PConfig) -> Iterator[PConfig]:
    for index, item in enumerate(config.items):
        if item.infinite:
            continue
        branches = _split_positive(item.repeats, config.assumptions)
        if branches is None:
            raise _UnknownBranch(
                f"cannot decide whether repeat count {item.repeats} is zero"
            )
        needs_branch = len(branches) > 1 or branches[0][1] or (
            branches[0][0] != config.assumptions
        )
        if needs_branch:
            for assumptions, is_zero in branches:
                branch = config.clone()
                branch.assumptions = assumptions
                if is_zero:
                    del branch.items[index]
                    if index < branch.boundary:
                        branch.boundary -= 1
                yield from _pnorm(branch)
            return

    merged: list[PItem] = []
    new_boundary = config.boundary
    for index, item in enumerate(config.items):
        item = item.substituted(config.assumptions)
        can_merge = (
            merged
            and not item.infinite
            and not merged[-1].infinite
            and item.word == merged[-1].word
            and index != config.boundary  # never merge across the head
        )
        if can_merge:
            previous = merged[-1]
            merged[-1] = PItem(previous.word, previous.repeats + item.repeats)
            if index < config.boundary:
                new_boundary -= 1
        else:
            merged.append(item)
    out = config.clone()
    out.items = merged
    out.boundary = new_boundary
    yield out


def _traverse_word(
    table: Table, state: int, word: tuple[int, ...], facing: int
) -> tuple:
    """Simulate one finite word entered from the side ``facing`` points to.

    Returns ``("exit", side, state, new_word, steps)``,
    ``("halt", new_word, steps)``, ``("undef", state, symbol)``, or
    ``("loop",)``.  A repeated ``(position, state, cells)`` proves a loop by
    the pigeonhole principle on the finite word.
    """
    cells_now = list(word)
    position = 0 if facing > 0 else len(cells_now) - 1
    current = state
    steps = 0
    seen: set[tuple[int, int, tuple[int, ...]]] = set()
    while True:
        key = (position, current, tuple(cells_now))
        if key in seen:
            return ("loop",)
        seen.add(key)
        if not (0 <= current < len(table)):
            return ("undef", current, cells_now[position])
        entry = table[current][cells_now[position]]
        if entry is None:
            return ("undef", current, cells_now[position])
        write, direction, next_state = entry
        cells_now[position] = write
        steps += 1
        if next_state == HALT:
            return ("halt", tuple(cells_now), steps)
        position += direction
        current = next_state
        if position < 0:
            return ("exit", -1, current, tuple(cells_now), steps)
        if position >= len(cells_now):
            return ("exit", 1, current, tuple(cells_now), steps)
        if steps > 100_000:  # a finite word must repeat a key far sooner
            return ("loop",)


class _HaltBranch(Exception):
    def __init__(self, steps: Expr, config: PConfig):
        super().__init__("halt")
        self.steps = steps
        self.config = config


def _pstep(config: PConfig, table: Table) -> Iterator[PConfig]:
    index = config.boundary if config.facing > 0 else config.boundary - 1
    item = config.items[index]
    if item.infinite:
        branch = config.clone()
        if config.facing > 0:
            branch.items.insert(config.boundary, PItem((0,), Expr.constant(1)))
        else:
            branch.items.insert(config.boundary - 1, PItem((0,), Expr.constant(1)))
            branch.boundary += 1
        branch.depth += 1
        yield from _pnorm(branch)
        return

    outcome = _traverse_word(table, config.state, item.word, config.facing)
    if outcome[0] == "undef":
        _, bad_state, symbol = outcome
        label = chr(65 + bad_state) if 0 <= bad_state < 26 else str(bad_state)
        raise _UnknownBranch(f"unassigned transition {label}{symbol} is reachable")
    if outcome[0] == "loop":
        raise _CounterexampleBranch("the machine loops inside a finite tape word")
    if outcome[0] == "halt":
        _, _new_word, used = outcome
        raise _HaltBranch(config.steps + used, config)

    _, exit_side, next_state, new_word, used = outcome
    through = exit_side == config.facing
    if through and next_state == config.state:
        branch = config.clone()
        branch.items[index] = PItem(new_word, item.repeats)
        branch.steps = branch.steps + item.repeats.scale(used)
        branch.depth += 1
        branch.boundary = index + 1 if config.facing > 0 else index
        branch.facing = config.facing
        yield from _pnorm(branch)
        return

    branches = _split_positive(item.repeats - 1, config.assumptions)
    if branches is None:
        raise _UnknownBranch(
            f"cannot peel one repetition from repeat count {item.repeats}"
        )
    for assumptions, remainder_zero in branches:
        branch = config.clone()
        branch.assumptions = assumptions
        branch.state = next_state
        branch.steps = branch.steps + used
        branch.depth += 1
        peeled = PItem(new_word, Expr.constant(1))
        if remainder_zero:
            branch.items[index] = peeled
            peeled_index = index
        elif config.facing > 0:
            branch.items[index : index + 1] = [
                peeled,
                PItem(item.word, item.repeats - 1),
            ]
            peeled_index = index
        else:
            branch.items[index : index + 1] = [
                PItem(item.word, item.repeats - 1),
                peeled,
            ]
            peeled_index = index + 1
        branch.boundary = peeled_index + 1 if exit_side > 0 else peeled_index
        branch.facing = exit_side
        yield from _pnorm(branch)


def _find_cycle(config: PConfig):
    """Find an ancestor snapshot forming a constant-delta repeat cycle.

    Returns ``(snapshot, deltas, segment_length)`` where ``deltas`` is the
    per-item constant change in repeat counts over one cycle, or ``None``.
    """
    current_assump = tuple(sorted(config.assumptions.items()))
    for snap in reversed(config.history):
        state, boundary, facing, items, assumptions, depth = snap
        if (state, boundary, facing) != (config.state, config.boundary, config.facing):
            continue
        if assumptions != current_assump or len(items) != len(config.items):
            continue
        if config.depth - depth < 1:
            continue
        deltas: list[int] = []
        ok = True
        for old, new in zip(items, config.items):
            if old.word != new.word or old.infinite != new.infinite:
                ok = False
                break
            diff = new.repeats.substitute(config.assumptions) - old.repeats.substitute(
                config.assumptions
            )
            if diff.terms:
                ok = False
                break
            deltas.append(diff.const)
        if ok and any(delta < 0 for delta in deltas) and any(deltas):
            return snap, deltas, config.depth - depth
    return None


def _prove_cycle(
    table: Table, snap, segment_length: int, deltas: list[int], attempt: int
) -> dict[int, int] | None:
    """Re-prove one cycle with fresh variables for the changing repeats.

    On success returns per-item thresholds: the cycle transformation is
    valid whenever each changing repeat is at least its threshold at the
    cycle start (other assumptions unchanged).  This is the induction step
    that justifies iterating the cycle many times at once.
    """
    state, boundary, facing, items, assumptions_t, depth = snap
    base_assumptions = dict(assumptions_t)
    changing = [i for i, delta in enumerate(deltas) if delta != 0]
    fresh: dict[int, str] = {}
    generic_items: list[PItem] = []
    generic_assumptions = dict(base_assumptions)
    for index, item in enumerate(items):
        if index in changing and not item.infinite:
            name = f"_cyc{attempt}_{index}"
            fresh[index] = name
            minimum = item.repeats.min_value(base_assumptions)
            if minimum is None:
                return None
            generic_assumptions[name] = ("ge", max(0, minimum))
            generic_items.append(PItem(item.word, Expr.var(name), item.infinite))
        else:
            generic_items.append(item)
    generic = PConfig(
        items=generic_items,
        boundary=boundary,
        facing=facing,
        state=state,
        assumptions=generic_assumptions,
        depth=depth,
    )
    target_depth = depth + segment_length
    try:
        stack = list(_pnorm(generic))
    except _UnknownBranch:
        return None
    explored = 0
    while stack and explored < 2_000:
        cfg = stack.pop()
        explored += 1
        key = cfg.canonical_key()
        if key in cfg.visited:
            continue
        cfg.visited = cfg.visited | {key}
        if cfg.depth == target_depth:
            if (cfg.state, cfg.boundary, cfg.facing) != (state, boundary, facing):
                continue
            if len(cfg.items) != len(items):
                continue
            # Original variables must be unrefined; fresh ones must be
            # lower bounds (not equalities) to serve as thresholds.
            if any(
                cfg.assumptions.get(name) != value
                for name, value in base_assumptions.items()
            ):
                continue
            thresholds: dict[int, int] = {}
            valid = True
            for index, (old, new) in enumerate(zip(items, cfg.items)):
                if old.word != new.word or old.infinite != new.infinite:
                    valid = False
                    break
                new_repeats = new.repeats.substitute(cfg.assumptions)
                if index in fresh:
                    expected = Expr.var(fresh[index]) + deltas[index]
                    if new_repeats != expected.substitute(cfg.assumptions):
                        valid = False
                        break
                    kind, value = cfg.assumptions.get(fresh[index], ("ge", 0))
                    if kind != "ge":
                        valid = False
                        break
                    thresholds[index] = value
                elif new_repeats != old.repeats.substitute(base_assumptions):
                    valid = False
                    break
            if valid:
                return thresholds
            continue
        if cfg.depth > target_depth:
            continue
        try:
            stack.extend(_pstep(cfg, table))
        except (_HaltBranch, _UnknownBranch, _CounterexampleBranch):
            continue
    return None


def _try_accelerate(
    table: Table,
    config: PConfig,
    snap,
    deltas: list[int],
    segment_length: int,
    thresholds: dict[int, int],
) -> list[PConfig] | None:
    """Jump ``config`` forward by many proved cycle iterations at once."""
    changing = [i for i, delta in enumerate(deltas) if delta != 0]
    decreasing = [i for i in changing if deltas[i] < 0]
    repeats = [
        item.repeats.substitute(config.assumptions) for item in config.items
    ]
    for driver in decreasing:
        step = -deltas[driver]
        diff = repeats[driver] - thresholds[driver]
        minimum = diff.min_value(config.assumptions)
        if minimum is None or minimum < 0:
            continue
        if any(coeff % step for _, coeff in diff.terms) or diff.const % step:
            continue
        iterations = Expr.from_terms(
            {name: coeff // step for name, coeff in diff.terms}, diff.const // step
        ) + 1
        if (iterations.min_value(config.assumptions) or 0) < 1:
            continue
        landings: dict[int, Expr] = {}
        valid = True
        for index in changing:
            landed = repeats[index] + iterations.scale(deltas[index])
            if (landed.min_value(config.assumptions) or -1) < 0:
                valid = False
                break
            if deltas[index] < 0:
                last_start = repeats[index] + (iterations - 1).scale(deltas[index])
                if (last_start - thresholds[index]).min_value(
                    config.assumptions
                ) is None or (last_start - thresholds[index]).min_value(
                    config.assumptions
                ) < 0:
                    valid = False
                    break
            elif (repeats[index] - thresholds[index]).min_value(
                config.assumptions
            ) is None or (repeats[index] - thresholds[index]).min_value(
                config.assumptions
            ) < 0:
                valid = False
                break
            landings[index] = landed
        if not valid:
            continue
        landing = config.clone()
        for index, landed in landings.items():
            old = landing.items[index]
            landing.items[index] = PItem(old.word, landed, old.infinite)
        landing.steps_known = False
        landing.depth = config.depth + segment_length
        try:
            return list(_pnorm(landing))
        except _UnknownBranch:
            return None
    return None


@dataclass(frozen=True)
class PatternRule:
    name: str
    initial: tuple[PItem, ...]
    expected: tuple[PItem, ...] | None  # None means halt is expected
    assumptions: Assumptions
    checkpoint_state: int = 0


def _split_sign(
    expr: Expr, assumptions: Assumptions
) -> list[tuple[Assumptions, int]] | None:
    """Covering branches for the sign of ``expr`` (-1, 0, or +1)."""
    expr = expr.substitute(assumptions)
    if expr.definitely_zero(assumptions):
        return [(dict(assumptions), 0)]
    if expr.definitely_positive(assumptions):
        return [(dict(assumptions), 1)]
    negative = (-expr).definitely_positive(assumptions)
    if negative:
        return [(dict(assumptions), -1)]
    if not expr.terms:
        return [(dict(assumptions), (expr.const > 0) - (expr.const < 0))]
    if len(expr.terms) != 1:
        return None
    (name, coeff), = expr.terms
    if coeff < 0:
        flipped = _split_sign(-expr, assumptions)
        if flipped is None:
            return None
        return [(assump, -sign) for assump, sign in flipped]
    # coeff > 0: expr == 0 iff x == target (when divisible).
    branches: list[tuple[Assumptions, int]] = []
    from .symbolic import _ceil_div, _lower_bound, _set_eq, _set_ge

    if (-expr.const) % coeff == 0:
        refined = _set_eq(assumptions, name, (-expr.const) // coeff)
        if refined is not None:
            branches.append((refined, 0))
    threshold = _ceil_div(1 - expr.const, coeff)
    refined = _set_ge(assumptions, name, threshold)
    if refined is not None and expr.definitely_positive(refined):
        branches.append((refined, 1))
    # Negative arm: x <= ceil((-1-const)/coeff); enumerate when short.
    upper = _ceil_div(-1 - expr.const, coeff)
    if (-1 - expr.const) % coeff == 0:
        upper = (-1 - expr.const) // coeff
    else:
        upper = (-1 - expr.const) // coeff  # floor for possibly negative numerator
    lower = _lower_bound(assumptions, name)
    if upper - lower > 16:
        return None
    for value in range(lower, upper + 1):
        refined = _set_eq(assumptions, name, value)
        if refined is not None:
            branches.append((refined, -1))
    return branches or None


def _drop_zero_right(
    items: list[PItem], assumptions: Assumptions
) -> Iterator[tuple[list[PItem], Assumptions]]:
    if not items:
        yield items, assumptions
        return
    item = items[-1]
    if item.infinite:
        yield items, assumptions
        return
    branches = _split_positive(item.repeats, assumptions)
    if branches is None:
        raise _UnknownBranch("cannot decide a repeat count while matching tapes")
    for assump, is_zero in branches:
        if is_zero:
            yield from _drop_zero_right(items[:-1], assump)
        else:
            yield items, assump


def _consume_suffix(
    items: list[PItem], count: int, assumptions: Assumptions
) -> Iterator[tuple[list[PItem], Assumptions]]:
    """Remove ``count`` cells from the right end of an item list."""
    item = items[-1]
    word, repeats = item.word, item.repeats
    if count == len(word):
        branches = _split_positive(repeats - 1, assumptions)
        if branches is None:
            raise _UnknownBranch("cannot peel a repetition while matching tapes")
        for assump, zero in branches:
            if zero:
                yield items[:-1], assump
            else:
                yield [*items[:-1], PItem(word, repeats - 1)], assump
        return
    prefix = word[:-count]
    branches = _split_positive(repeats - 1, assumptions)
    if branches is None:
        raise _UnknownBranch("cannot peel a repetition while matching tapes")
    for assump, zero in branches:
        if zero:
            yield [*items[:-1], PItem(prefix, Expr.constant(1))], assump
        else:
            yield [
                *items[:-1],
                PItem(word, repeats - 1),
                PItem(prefix, Expr.constant(1)),
            ], assump


def _trim_leading_zeros(
    items: list[PItem], assumptions: Assumptions
) -> Iterator[tuple[list[PItem], Assumptions]]:
    """Drop blank cells before the first 1 (translation invariance)."""
    if not items:
        yield items, assumptions
        return
    item = items[0]
    if item.infinite:
        yield from _trim_leading_zeros(items[1:], assumptions)
        return
    if all(cell == 0 for cell in item.word):
        yield from _trim_leading_zeros(items[1:], assumptions)
        return
    if item.word[0] == 1:
        yield items, assumptions
        return
    # Drop the first cell (a zero) of the first repetition.
    branches = _split_positive(item.repeats - 1, assumptions)
    if branches is None:
        raise _UnknownBranch("cannot trim a leading zero while matching tapes")
    for assump, zero in branches:
        head = PItem(item.word[1:], Expr.constant(1))
        if zero:
            yield from _trim_leading_zeros([head, *items[1:]], assump)
        else:
            yield from _trim_leading_zeros(
                [head, PItem(item.word, item.repeats - 1), *items[1:]], assump
            )


def _tapes_equal(
    left: list[PItem],
    right: list[PItem],
    assumptions: Assumptions,
    *,
    budget: int = 300,
) -> Iterator[tuple[Assumptions, bool]]:
    """Branching equality test for two symbolic item expansions."""
    if budget <= 0:
        raise _UnknownBranch("tape matching bound reached")
    for left0, assump0 in _trim_leading_zeros(left, assumptions):
        for right0, assump1 in _trim_leading_zeros(right, assump0):
            for left1, assump2 in _drop_zero_right(left0, assump1):
                for right1, assump3 in _drop_zero_right(right0, assump2):
                    yield from _tapes_equal_inner(left1, right1, assump3, budget)


def _tapes_equal_inner(left, right, assumptions, budget):
    if budget <= 0:
        raise _UnknownBranch("tape matching bound reached")
    if not left and not right:
        yield assumptions, True
        return
    if not left or not right:
        yield assumptions, False
        return
    a_item, b_item = left[-1], right[-1]
    if a_item.infinite or b_item.infinite:
        yield assumptions, a_item.infinite and b_item.infinite
        return
    wa, wb = a_item.word, b_item.word
    if len(wa) == len(wb):
        if wa != wb:
            yield assumptions, False
            return
        signs = _split_sign(a_item.repeats - b_item.repeats, assumptions)
        if signs is None:
            raise _UnknownBranch(
                "cannot compare repeat counts "
                f"{a_item.repeats} and {b_item.repeats}"
            )
        for assump, sign in signs:
            if sign == 0:
                yield from _tapes_equal(left[:-1], right[:-1], assump, budget=budget - 1)
            elif sign > 0:
                rest = PItem(wa, (a_item.repeats - b_item.repeats).substitute(assump))
                yield from _tapes_equal([*left[:-1], rest], right[:-1], assump, budget=budget - 1)
            else:
                rest = PItem(wb, (b_item.repeats - a_item.repeats).substitute(assump))
                yield from _tapes_equal(left[:-1], [*right[:-1], rest], assump, budget=budget - 1)
        return
    count = min(len(wa), len(wb))
    if wa[-count:] != wb[-count:]:
        yield assumptions, False
        return
    for left2, assump1 in _consume_suffix(left, count, assumptions):
        for right2, assump2 in _consume_suffix(right, count, assump1):
            yield from _tapes_equal(left2, right2, assump2, budget=budget - 1)


def _canonical_pattern(
    items: list[PItem], assumptions: Assumptions
) -> tuple[tuple[tuple[int, ...], Expr], ...] | None:
    merged: list[tuple[tuple[int, ...], Expr]] = []
    for item in items:
        if item.infinite:
            continue
        if item.repeats.definitely_zero(assumptions):
            continue
        if not item.repeats.definitely_positive(assumptions):
            return None
        repeats = item.repeats.substitute(assumptions)
        if merged and merged[-1][0] == item.word:
            merged[-1] = (item.word, merged[-1][1] + repeats)
        else:
            merged.append((item.word, repeats))
    return tuple(merged)


def _pattern_text(pattern) -> str:
    if pattern is None:
        return "<undecidable pattern>"
    return " ".join(
        f"({''.join(str(c) for c in word)})^({repeats})"
        for word, repeats in pattern
    )


def _pbranch(
    rule: PatternRule, config: PConfig, status: str, reason: str, steps=None
) -> BranchResult:
    if config.steps_known:
        steps_text = str(steps if steps is not None else config.steps)
    else:
        steps_text = "accelerated; exact count not tracked"
    return BranchResult(
        case_name=rule.name,
        assumptions=dict(config.assumptions),
        status=status,
        reason=reason,
        steps=steps_text,
        final=config.render(),
    )


def verify_pattern_rule(
    table: Table,
    rule: PatternRule,
    *,
    max_symbolic_steps: int = 300,
    max_branches: int = 4_000,
) -> SymbolicResult:
    """Verify one right-edge checkpoint rule over repeated tape words."""
    if not (0 <= rule.checkpoint_state < len(table)):
        raise ValueError("checkpoint_state is outside the transition table")
    initial = PConfig(
        items=[_psentinel(), *rule.initial, _psentinel()],
        boundary=len(rule.initial) + 1,
        facing=1,
        state=rule.checkpoint_state,
        assumptions=dict(rule.assumptions),
    )
    results: list[BranchResult] = []
    stack: list[PConfig] = []
    try:
        stack.extend(_pnorm(initial))
    except _UnknownBranch as exc:
        results.append(_pbranch(rule, initial, "unknown", str(exc)))

    explored = 0
    hit_bound = False
    cycle_cache: dict = {}
    accel_attempts = 0
    while stack:
        if explored >= max_branches:
            hit_bound = True
            break
        config = stack.pop()
        explored += 1
        key = config.canonical_key()
        if key in config.visited:
            results.append(
                _pbranch(rule, config, "counterexample", "symbolic configuration repeats")
            )
            continue
        config.visited = config.visited | {key}

        at_checkpoint = (
            config.depth > 0
            and config.state == rule.checkpoint_state
            and config.facing > 0
            and config.boundary == len(config.items) - 1
            and config.items[-1].infinite
        )
        # A right-edge visit in the checkpoint state is only a candidate
        # endpoint: champion rules pass through many such visits.  The
        # branch is proved when the tape first equals the expected pattern
        # at such a visit; non-matching visits continue executing.  (That
        # no *other* checkpoint-shaped form intervenes must be established
        # separately, e.g. by concrete checkpoint parsing.)
        to_step = [config]
        if at_checkpoint and rule.expected is not None:
            to_step = []
            finite = [item for item in config.items if not item.infinite]
            try:
                matches = list(
                    _tapes_equal(finite, list(rule.expected), config.assumptions)
                )
            except _UnknownBranch as exc:
                results.append(_pbranch(rule, config, "unknown", str(exc)))
                continue
            for assump, equal in matches:
                clone = config.clone()
                clone.assumptions = assump
                if equal:
                    expected_pattern = _canonical_pattern(
                        list(rule.expected), assump
                    )
                    results.append(
                        _pbranch(
                            rule,
                            clone,
                            "proved",
                            "tape matches the expected pattern: "
                            f"{_pattern_text(expected_pattern)}",
                        )
                    )
                else:
                    to_step.append(clone)
            if not to_step:
                continue

        if config.depth > max_symbolic_steps:
            results.append(
                _pbranch(rule, config, "unknown", "symbolic step bound reached")
            )
            continue
        for stepping in to_step:
            # Counter-induction acceleration: if this configuration repeats
            # an ancestor's shape with constant repeat-count deltas, try to
            # jump many iterations at once (proved generically first).
            accelerated = False
            cycle = _find_cycle(stepping)
            if cycle is not None and accel_attempts < 200:
                snap, deltas, segment_length = cycle
                shape = (
                    snap[0],
                    snap[1],
                    snap[2],
                    tuple(item.word for item in snap[3]),
                    tuple(
                        item.repeats.substitute(dict(snap[4])) for item in snap[3]
                    ),
                    snap[4],
                    tuple(deltas),
                    segment_length,
                )
                if shape not in stepping.accel_tried:
                    stepping.accel_tried = stepping.accel_tried | {shape}
                    if shape in cycle_cache:
                        thresholds = cycle_cache[shape]
                    else:
                        accel_attempts += 1
                        thresholds = _prove_cycle(
                            table, snap, segment_length, deltas, accel_attempts
                        )
                        cycle_cache[shape] = thresholds
                    if thresholds is not None:
                        landings = _try_accelerate(
                            table, stepping, snap, deltas, segment_length, thresholds
                        )
                        if landings:
                            for landing in landings:
                                landing.history = stepping.history + (
                                    stepping.snapshot(),
                                )
                                landing.accel_tried = stepping.accel_tried
                                stack.append(landing)
                            accelerated = True
            if accelerated:
                continue
            try:
                for successor in _pstep(stepping, table):
                    successor.history = stepping.history + (stepping.snapshot(),)
                    successor.accel_tried = stepping.accel_tried
                    stack.append(successor)
            except _HaltBranch as halt:
                if rule.expected is None:
                    results.append(
                        _pbranch(
                            rule, halt.config, "proved", "halts as required", halt.steps
                        )
                    )
                else:
                    results.append(
                        _pbranch(
                            rule,
                            halt.config,
                            "counterexample",
                            "halts before the required checkpoint",
                            halt.steps,
                        )
                    )
            except _UnknownBranch as exc:
                results.append(_pbranch(rule, stepping, "unknown", str(exc)))
            except _CounterexampleBranch as exc:
                results.append(_pbranch(rule, stepping, "counterexample", str(exc)))

    if hit_bound and stack:
        results.append(
            _pbranch(rule, stack[-1], "unknown", "symbolic branch bound reached")
        )
    if any(branch.status == "counterexample" for branch in results):
        status = "counterexample"
    elif results and all(branch.status == "proved" for branch in results):
        status = "proved"
    else:
        status = "unknown"
    return SymbolicResult(status=status, branches=tuple(results), explored=explored)
