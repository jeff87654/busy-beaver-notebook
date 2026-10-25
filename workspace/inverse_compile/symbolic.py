"""Symbolic verification of one abstract counter step for all block sizes.

The tape is represented by run-length segments whose lengths are affine
expressions in the abstract values ``n, d0, d1, ...``.  A self-loop that moves
consistently in one direction is executed as one shift rule over an entire
run; this is the induction step that makes a proof for arbitrary block
lengths possible.  Other transitions are executed one cell at a time.

A result is deliberately three-valued:

* ``proved`` — every case branch reaches the required checkpoint or halt
  with exactly the expected symbolic tape;
* ``counterexample`` — some feasible case reaches a wrong terminal form or
  provably drifts/loops forever;
* ``unknown`` — the executor hit an unassigned transition, an expression it
  could not split soundly, or a search bound.

Only one abstract step is proved here.  Iterating the step and deriving a
growth bound additionally require the abstract counter's termination and
domination lemmas.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from .abstract import TemplateParams
from .encoding import BlockEncoding
from .tm import HALT, Table

Assumptions = dict[str, tuple[str, int]]  # variable -> ("ge", k) / ("eq", k)


def _ceil_div(p: int, q: int) -> int:
    return -((-p) // q)


@dataclass(frozen=True)
class Expr:
    """An affine integer expression with canonically sorted terms."""

    terms: tuple[tuple[str, int], ...] = ()
    const: int = 0

    @staticmethod
    def constant(value: int) -> "Expr":
        return Expr((), int(value))

    @staticmethod
    def var(name: str) -> "Expr":
        return Expr(((name, 1),), 0)

    @staticmethod
    def from_terms(terms: dict[str, int], const: int = 0) -> "Expr":
        clean = tuple(sorted((k, v) for k, v in terms.items() if v))
        return Expr(clean, int(const))

    def __add__(self, other: "Expr | int") -> "Expr":
        if isinstance(other, int):
            return Expr(self.terms, self.const + other)
        terms = dict(self.terms)
        for name, coeff in other.terms:
            terms[name] = terms.get(name, 0) + coeff
        return Expr.from_terms(terms, self.const + other.const)

    __radd__ = __add__

    def __neg__(self) -> "Expr":
        return Expr(tuple((k, -v) for k, v in self.terms), -self.const)

    def __sub__(self, other: "Expr | int") -> "Expr":
        if isinstance(other, int):
            return Expr(self.terms, self.const - other)
        return self + (-other)

    def scale(self, factor: int) -> "Expr":
        return Expr.from_terms(
            {k: v * factor for k, v in self.terms}, self.const * factor
        )

    def substitute(self, assumptions: Assumptions) -> "Expr":
        terms: dict[str, int] = {}
        const = self.const
        for name, coeff in self.terms:
            kind, value = assumptions.get(name, ("ge", 0))
            if kind == "eq":
                const += coeff * value
            else:
                terms[name] = coeff
        return Expr.from_terms(terms, const)

    def min_value(self, assumptions: Assumptions) -> int | None:
        expr = self.substitute(assumptions)
        total = expr.const
        for name, coeff in expr.terms:
            if coeff < 0:
                return None
            total += coeff * assumptions.get(name, ("ge", 0))[1]
        return total

    def max_value(self, assumptions: Assumptions) -> int | None:
        expr = self.substitute(assumptions)
        total = expr.const
        for name, coeff in expr.terms:
            if coeff > 0:
                return None
            total += coeff * assumptions.get(name, ("ge", 0))[1]
        return total

    def definitely_zero(self, assumptions: Assumptions) -> bool:
        expr = self.substitute(assumptions)
        return not expr.terms and expr.const == 0

    def definitely_positive(self, assumptions: Assumptions) -> bool:
        minimum = self.min_value(assumptions)
        return minimum is not None and minimum >= 1

    def __str__(self) -> str:
        parts: list[str] = []
        for name, coeff in self.terms:
            if coeff == 1:
                parts.append(name)
            elif coeff == -1:
                parts.append(f"-{name}")
            else:
                parts.append(f"{coeff}*{name}")
        if self.const or not parts:
            parts.append(str(self.const))
        text = "+".join(parts).replace("+-", "-")
        return text


def _lower_bound(assumptions: Assumptions, name: str) -> int:
    return assumptions.get(name, ("ge", 0))[1]


def _set_eq(assumptions: Assumptions, name: str, value: int) -> Assumptions | None:
    kind, old = assumptions.get(name, ("ge", 0))
    if kind == "eq":
        return dict(assumptions) if old == value else None
    if value < old:
        return None
    out = dict(assumptions)
    out[name] = ("eq", value)
    return out


def _set_ge(assumptions: Assumptions, name: str, value: int) -> Assumptions | None:
    kind, old = assumptions.get(name, ("ge", 0))
    if kind == "eq":
        return dict(assumptions) if old >= value else None
    out = dict(assumptions)
    out[name] = ("ge", max(old, value))
    return out


def _split_positive(
    expr: Expr, assumptions: Assumptions
) -> list[tuple[Assumptions, bool]] | None:
    """Covering branches for ``expr == 0`` versus ``expr > 0``.

    Each result is ``(refined assumptions, is_zero)``.  ``None`` means that
    this deliberately small arithmetic layer cannot split the expression
    soundly, so the caller must report ``unknown`` rather than guess.
    """
    expr = expr.substitute(assumptions)
    if expr.definitely_zero(assumptions):
        return [(dict(assumptions), True)]
    if expr.definitely_positive(assumptions):
        return [(dict(assumptions), False)]
    if not expr.terms:
        return [(dict(assumptions), expr.const == 0)]

    if len(expr.terms) == 1:
        (name, coeff), = expr.terms
        const = expr.const
        branches: list[tuple[Assumptions, bool]] = []
        # Zero arm: coeff*x + const == 0.
        numerator = -const
        if numerator % coeff == 0:
            refined = _set_eq(assumptions, name, numerator // coeff)
            if refined is not None:
                branches.append((refined, True))
        if coeff > 0:
            threshold = _ceil_div(1 - const, coeff)
            refined = _set_ge(assumptions, name, threshold)
            if refined is not None:
                # If the variable was already fixed, definiteness above has
                # normally handled it; keep only a genuinely positive arm.
                if Expr(expr.terms, const).definitely_positive(refined):
                    branches.append((refined, False))
        else:
            # Positive means x <= upper; enumerate the finitely many small
            # possibilities when that interval is short.
            upper = (const - 1) // (-coeff)
            lower = _lower_bound(assumptions, name)
            if upper - lower > 16:
                return None
            for value in range(lower, upper + 1):
                refined = _set_eq(assumptions, name, value)
                if refined is not None:
                    branches.append((refined, False))
        return branches or None

    # Several variables with nonnegative coefficients and minimum zero:
    # the zero arm forces every variable to its lower bound, and the
    # positive arm is covered (with harmless overlap) by choosing one
    # variable that exceeds its bound.
    if all(coeff > 0 for _, coeff in expr.terms):
        minimum = expr.min_value(assumptions)
        if minimum == 0:
            branches = []
            zero_assumptions: Assumptions | None = dict(assumptions)
            for name, _ in expr.terms:
                if zero_assumptions is None:
                    break
                zero_assumptions = _set_eq(
                    zero_assumptions, name, _lower_bound(assumptions, name)
                )
            if zero_assumptions is not None:
                branches.append((zero_assumptions, True))
            for name, _ in expr.terms:
                refined = _set_ge(
                    assumptions, name, _lower_bound(assumptions, name) + 1
                )
                if refined is not None:
                    branches.append((refined, False))
            return branches or None
    return None


class _UnknownBranch(Exception):
    pass


class _CounterexampleBranch(Exception):
    pass


@dataclass(frozen=True)
class Segment:
    symbol: int
    length: Expr
    infinite: bool = False
    tag: str = ""

    def substituted(self, assumptions: Assumptions) -> "Segment":
        return Segment(
            self.symbol, self.length.substitute(assumptions), self.infinite, ""
        )


def _sentinel() -> Segment:
    return Segment(0, Expr.constant(0), infinite=True)


@dataclass
class SymConfig:
    segments: list[Segment]
    head: int  # index of the one-cell head segment
    state: int
    assumptions: Assumptions
    steps: Expr = Expr.constant(0)
    depth: int = 0
    visited: frozenset = frozenset()
    case_name: str = ""
    expected: tuple[Expr, ...] | None = None  # None means halt is expected

    def clone(self) -> "SymConfig":
        return SymConfig(
            list(self.segments),
            self.head,
            self.state,
            dict(self.assumptions),
            self.steps,
            self.depth,
            self.visited,
            self.case_name,
            self.expected,
        )

    def read(self) -> int:
        return self.segments[self.head].symbol

    def canonical_key(self):
        segments = tuple(
            (
                segment.symbol,
                segment.length.substitute(self.assumptions),
                segment.infinite,
            )
            for segment in self.segments
        )
        assumptions = tuple(sorted(self.assumptions.items()))
        return (self.state, self.head, segments, assumptions)

    def render(self) -> str:
        parts: list[str] = []
        for index, segment in enumerate(self.segments):
            if segment.infinite:
                parts.append("0^inf")
                continue
            text = f"{segment.symbol}^({segment.length.substitute(self.assumptions)})"
            parts.append(f"[{text}]" if index == self.head else text)
        state = "Z" if self.state == HALT else chr(65 + self.state)
        return f"{state}: " + " ".join(parts)


def _normalize(config: SymConfig) -> Iterator[SymConfig]:
    """Drop zero-length finite runs and merge adjacent non-head runs.

    Branching refinements of the assumptions are yielded as separate
    configurations whenever a run length is not yet known to be positive.
    """
    # Resolve one undecided or zero length at a time.
    for index, segment in enumerate(config.segments):
        if segment.infinite or index == config.head:
            continue
        branches = _split_positive(segment.length, config.assumptions)
        if branches is None:
            raise _UnknownBranch(
                f"cannot decide whether run length {segment.length} is zero"
            )
        needs_branch = len(branches) > 1 or branches[0][1] or (
            branches[0][0] != config.assumptions
        )
        if needs_branch:
            for assumptions, is_zero in branches:
                branch = config.clone()
                branch.assumptions = assumptions
                if is_zero:
                    del branch.segments[index]
                    if index < branch.head:
                        branch.head -= 1
                yield from _normalize(branch)
            return

    merged: list[Segment] = []
    new_head = config.head
    for index, segment in enumerate(config.segments):
        segment = segment.substituted(config.assumptions)
        can_merge = (
            merged
            and not segment.infinite
            and not merged[-1].infinite
            and segment.symbol == merged[-1].symbol
            and index != config.head
            and len(merged) - 1 != new_head
        )
        if can_merge:
            previous = merged[-1]
            merged[-1] = Segment(
                previous.symbol, previous.length + segment.length
            )
            if index < config.head:
                new_head -= 1
        else:
            if index == config.head:
                new_head = len(merged)
            merged.append(segment)
    out = config.clone()
    out.segments = merged
    out.head = new_head
    yield out


def _head_beyond(
    config: SymConfig, from_index: int, direction: int
) -> Iterator[SymConfig]:
    """Move the head marker to the first cell past ``from_index``."""
    neighbor_index = from_index + direction
    neighbor = config.segments[neighbor_index]
    if neighbor.infinite:
        branch = config.clone()
        insert_at = neighbor_index if direction > 0 else from_index
        branch.segments.insert(insert_at, Segment(0, Expr.constant(1)))
        branch.head = insert_at
        yield from _normalize(branch)
        return

    branches = _split_positive(neighbor.length - 1, config.assumptions)
    if branches is None:
        raise _UnknownBranch(
            f"cannot split neighboring run of length {neighbor.length}"
        )
    for assumptions, remainder_zero in branches:
        branch = config.clone()
        branch.assumptions = assumptions
        segment = branch.segments[neighbor_index]
        cell = Segment(segment.symbol, Expr.constant(1))
        if remainder_zero:
            branch.segments[neighbor_index] = cell
            branch.head = neighbor_index
        else:
            remainder = Segment(segment.symbol, segment.length - 1)
            if direction > 0:
                branch.segments[neighbor_index : neighbor_index + 1] = [
                    cell,
                    remainder,
                ]
                branch.head = neighbor_index
            else:
                branch.segments[neighbor_index : neighbor_index + 1] = [
                    remainder,
                    cell,
                ]
                branch.head = neighbor_index + 1
        yield from _normalize(branch)


def _single_step(
    config: SymConfig, write: int, direction: int, next_state: int
) -> Iterator[SymConfig]:
    branch = config.clone()
    branch.segments[branch.head] = Segment(write, Expr.constant(1))
    branch.state = next_state
    branch.steps = branch.steps + 1
    branch.depth += 1
    yield from _head_beyond(branch, branch.head, direction)


def _macro_step(
    config: SymConfig, write: int, direction: int
) -> Iterator[SymConfig]:
    """Execute a same-state sweep over the whole run under the head."""
    read_symbol = config.read()
    neighbor_index = config.head + direction
    neighbor = config.segments[neighbor_index]
    if neighbor.infinite and read_symbol == 0:
        raise _CounterexampleBranch(
            "a same-state sweep drifts forever over blank tape"
        )
    count = Expr.constant(1)
    consumed = False
    if not neighbor.infinite and neighbor.symbol == read_symbol:
        count = count + neighbor.length
        consumed = True

    branch = config.clone()
    if consumed:
        low = min(branch.head, neighbor_index)
        high = max(branch.head, neighbor_index)
        branch.segments[low : high + 1] = [Segment(write, count)]
        inserted = low
    else:
        branch.segments[branch.head] = Segment(write, count)
        inserted = branch.head
    branch.steps = branch.steps + count
    branch.depth += 1
    yield from _head_beyond(branch, inserted, direction)


Pattern = tuple[tuple[tuple[int, Expr], ...], Expr]


def _pattern_from_runs(
    runs: list[tuple[int, Expr]], head_coordinate: Expr, assumptions: Assumptions
) -> Pattern | None:
    merged: list[list] = []  # [symbol, length, start]
    coordinate = Expr.constant(0)
    for symbol, length in runs:
        if length.definitely_zero(assumptions):
            continue
        if not length.definitely_positive(assumptions):
            return None
        if merged and merged[-1][0] == symbol:
            merged[-1][1] = merged[-1][1] + length
        else:
            merged.append([symbol, length, coordinate])
        coordinate = coordinate + length
    one_indices = [i for i, run in enumerate(merged) if run[0] == 1]
    if not one_indices:
        return ((), Expr.constant(0))
    first, last = one_indices[0], one_indices[-1]
    pattern_runs = tuple(
        (int(run[0]), Expr(run[1].terms, run[1].const).substitute(assumptions))
        for run in merged[first : last + 1]
    )
    head_offset = (head_coordinate - merged[first][2]).substitute(assumptions)
    return (pattern_runs, head_offset)


def _final_pattern(config: SymConfig) -> Pattern | None:
    runs: list[tuple[int, Expr]] = []
    head_coordinate = Expr.constant(0)
    found_head = False
    for index, segment in enumerate(config.segments):
        if segment.infinite:
            continue
        if index == config.head:
            found_head = True
            head_coordinate = sum(
                (length for _, length in runs), Expr.constant(0)
            )
        runs.append((segment.symbol, segment.length))
    if not found_head:
        return None
    return _pattern_from_runs(runs, head_coordinate, config.assumptions)


def _expected_pattern(
    values: tuple[Expr, ...], encoding: BlockEncoding, assumptions: Assumptions
) -> Pattern | None:
    runs: list[tuple[int, Expr]] = []
    for index, value in enumerate(values):
        runs.append((1, value + encoding.offset))
        if index != len(values) - 1:
            runs.append((0, Expr.constant(1)))
    first_length = values[0] + encoding.offset
    if encoding.head_anchor == "left":
        head_coordinate = Expr.constant(0)
    elif first_length.definitely_zero(assumptions):
        head_coordinate = Expr.constant(0)
    elif first_length.definitely_positive(assumptions):
        head_coordinate = first_length - 1
    else:
        return None
    return _pattern_from_runs(runs, head_coordinate, assumptions)


def _pattern_text(pattern: Pattern | None) -> str:
    if pattern is None:
        return "<undecidable pattern>"
    runs, head_offset = pattern
    if not runs:
        return f"<blank; head offset {head_offset}>"
    text = " ".join(f"{symbol}^({length})" for symbol, length in runs)
    return f"{text}; head offset {head_offset}"


def _split_tagged_segment(
    segments: list[Segment], tag: str, offset: Expr, assumptions: Assumptions
) -> Iterator[tuple[list[Segment], int, Assumptions]]:
    index = next(i for i, segment in enumerate(segments) if segment.tag == tag)
    segment = segments[index]
    prefix_branches = _split_positive(offset, assumptions)
    if prefix_branches is None:
        raise _UnknownBranch(f"cannot split initial segment at offset {offset}")
    for assump1, prefix_zero in prefix_branches:
        suffix_length = segment.length - offset - 1
        suffix_branches = _split_positive(suffix_length, assump1)
        if suffix_branches is None:
            raise _UnknownBranch(
                f"cannot split initial segment with suffix {suffix_length}"
            )
        for assump2, suffix_zero in suffix_branches:
            replacement: list[Segment] = []
            if not prefix_zero:
                replacement.append(Segment(segment.symbol, offset))
            head = index + len(replacement)
            replacement.append(Segment(segment.symbol, Expr.constant(1)))
            if not suffix_zero:
                replacement.append(Segment(segment.symbol, suffix_length))
            out = list(segments)
            out[index : index + 1] = replacement
            yield out, head, assump2


def _build_initial(
    values: tuple[Expr, ...],
    encoding: BlockEncoding,
    phase_state: int,
    assumptions: Assumptions,
    case_name: str,
    expected: tuple[Expr, ...] | None,
) -> Iterator[SymConfig]:
    def tagged_segments() -> list[Segment]:
        segments = [_sentinel()]
        for index, value in enumerate(values):
            segments.append(
                Segment(1, value + encoding.offset, tag=f"block{index}")
            )
            if index != len(values) - 1:
                segments.append(
                    Segment(0, Expr.constant(1), tag=f"sep{index}")
                )
        segments.append(_sentinel())
        return segments

    first_length = values[0] + encoding.offset
    branches = _split_positive(first_length, assumptions)
    if branches is None:
        raise _UnknownBranch("cannot decide whether the first block is empty")
    for branch_assumptions, first_zero in branches:
        if first_zero:
            tag, offset = "sep0", Expr.constant(0)
        elif encoding.head_anchor == "n_right":
            tag, offset = "block0", first_length - 1
        else:
            tag, offset = "block0", Expr.constant(0)
        for segments, head, split_assumptions in _split_tagged_segment(
            tagged_segments(), tag, offset, branch_assumptions
        ):
            config = SymConfig(
                segments=segments,
                head=head,
                state=phase_state,
                assumptions=split_assumptions,
                case_name=case_name,
                expected=expected,
            )
            yield from _normalize(config)


@dataclass(frozen=True)
class BranchResult:
    case_name: str
    assumptions: Assumptions
    status: str  # proved, counterexample, unknown
    reason: str
    steps: str | None = None
    final: str | None = None


@dataclass(frozen=True)
class SymbolicResult:
    status: str  # proved, counterexample, unknown
    branches: tuple[BranchResult, ...]
    explored: int

    @property
    def proved(self) -> bool:
        return self.status == "proved"

    def by_case(self) -> dict[str, list[BranchResult]]:
        grouped: dict[str, list[BranchResult]] = {}
        for branch in self.branches:
            grouped.setdefault(branch.case_name, []).append(branch)
        return grouped


def _refill_expr(params: TemplateParams, n_expr: Expr) -> Expr:
    if params.refill == "n":
        return n_expr
    if params.refill == "n+c":
        return n_expr + params.refill_const
    return n_expr.scale(2) + params.refill_const


def _make_cases(
    n_digits: int, params: TemplateParams
) -> list[tuple[str, tuple[Expr, ...], Assumptions, tuple[Expr, ...] | None]]:
    n_expr = Expr.var("n")
    digits = tuple(Expr.var(f"d{index}") for index in range(n_digits))
    values = (n_expr,) + digits
    base: Assumptions = {"n": ("ge", 0)}
    for index in range(n_digits):
        base[f"d{index}"] = ("ge", 0)

    cases = []
    for lowest in range(n_digits):
        assumptions = dict(base)
        for index in range(lowest):
            assumptions[f"d{index}"] = ("eq", 0)
        assumptions[f"d{lowest}"] = ("ge", 1)
        expected = list(values)
        if lowest == 0:
            name = "successor_d0"
            if params.successor == "double":
                expected[0] = n_expr.scale(2) + params.successor_const
            else:
                expected[0] = n_expr + params.increment
            expected[1] = digits[0] - 1
        else:
            name = f"refill_from_d{lowest}"
            expected[lowest] = _refill_expr(params, n_expr)
            expected[lowest + 1] = digits[lowest] - 1
            if params.consume_refill:
                expected[0] = Expr.constant(0)
        cases.append((name, values, assumptions, tuple(expected)))

    halt_assumptions = dict(base)
    for index in range(n_digits):
        halt_assumptions[f"d{index}"] = ("eq", 0)
    cases.append(("halt_all_zero", values, halt_assumptions, None))
    return cases


def _branch(
    config: SymConfig, status: str, reason: str, *, steps: Expr | None = None
) -> BranchResult:
    return BranchResult(
        case_name=config.case_name,
        assumptions=dict(config.assumptions),
        status=status,
        reason=reason,
        steps=str(steps if steps is not None else config.steps),
        final=config.render(),
    )


def verify_counter_step_symbolic(
    table: Table,
    *,
    n_digits: int,
    params: TemplateParams = TemplateParams(),
    encoding: BlockEncoding = BlockEncoding(),
    phase_state: int = 0,
    max_symbolic_steps: int = 100,
    max_branches: int = 2_000,
) -> SymbolicResult:
    """Prove one abstract step from every encoded symbolic configuration.

    The quantification is over every ``n`` and every digit vector of the
    given fixed length, under the chosen encoding and checkpoint phase.
    """
    if n_digits < 1:
        raise ValueError("n_digits must be positive")
    if not (0 <= phase_state < len(table)):
        raise ValueError("phase_state is outside the transition table")
    if n_digits > 1 and encoding.offset == 0:
        raise ValueError("offset-zero encodings are ambiguous for several digits")

    results: list[BranchResult] = []
    stack: list[SymConfig] = []
    for case_name, values, assumptions, expected in _make_cases(n_digits, params):
        seed = SymConfig(
            segments=[_sentinel(), _sentinel()],
            head=0,
            state=phase_state,
            assumptions=dict(assumptions),
            case_name=case_name,
            expected=expected,
        )
        try:
            stack.extend(
                _build_initial(
                    values, encoding, phase_state, assumptions, case_name, expected
                )
            )
        except _UnknownBranch as exc:
            results.append(_branch(seed, "unknown", str(exc)))

    explored = 0
    hit_branch_bound = False
    while stack:
        if explored >= max_branches:
            hit_branch_bound = True
            break
        config = stack.pop()
        explored += 1
        key = config.canonical_key()
        if key in config.visited:
            results.append(
                _branch(config, "counterexample", "symbolic configuration repeats")
            )
            continue
        config.visited = config.visited | {key}
        if config.depth > max_symbolic_steps:
            results.append(
                _branch(config, "unknown", "symbolic step bound reached")
            )
            continue
        if not (0 <= config.state < len(table)):
            results.append(
                _branch(
                    config,
                    "unknown",
                    f"transition leads outside the table to state {config.state}",
                )
            )
            continue

        symbol = config.read()
        entry = table[config.state][symbol]
        if entry is None:
            letter = chr(65 + config.state)
            results.append(
                _branch(
                    config,
                    "unknown",
                    f"unassigned transition {letter}{symbol} is reachable",
                )
            )
            continue
        write, direction, next_state = entry
        try:
            if next_state == HALT:
                if config.expected is None:
                    results.append(
                        _branch(
                            config,
                            "proved",
                            "halts from the all-zero digit case",
                            steps=config.steps + 1,
                        )
                    )
                else:
                    results.append(
                        _branch(
                            config,
                            "counterexample",
                            "halts before the required checkpoint",
                            steps=config.steps + 1,
                        )
                    )
            elif next_state == phase_state:
                for successor in _single_step(
                    config, write, direction, next_state
                ):
                    if config.expected is None:
                        results.append(
                            _branch(
                                successor,
                                "counterexample",
                                "reaches the checkpoint instead of halting",
                            )
                        )
                        continue
                    final_pattern = _final_pattern(successor)
                    expected_pattern = _expected_pattern(
                        config.expected, encoding, successor.assumptions
                    )
                    if final_pattern is None or expected_pattern is None:
                        results.append(
                            _branch(
                                successor,
                                "unknown",
                                "cannot decide the final tape pattern",
                            )
                        )
                    elif final_pattern == expected_pattern:
                        results.append(
                            _branch(
                                successor,
                                "proved",
                                f"final tape {_pattern_text(final_pattern)}",
                            )
                        )
                    else:
                        results.append(
                            _branch(
                                successor,
                                "counterexample",
                                "wrong checkpoint tape: got "
                                f"{_pattern_text(final_pattern)}, expected "
                                f"{_pattern_text(expected_pattern)}",
                            )
                        )
            elif next_state == config.state:
                stack.extend(_macro_step(config, write, direction))
            else:
                stack.extend(
                    _single_step(config, write, direction, next_state)
                )
        except _UnknownBranch as exc:
            results.append(_branch(config, "unknown", str(exc)))
        except _CounterexampleBranch as exc:
            results.append(_branch(config, "counterexample", str(exc)))

    if hit_branch_bound and stack:
        results.append(
            _branch(stack[-1], "unknown", "symbolic branch bound reached")
        )
    if any(branch.status == "counterexample" for branch in results):
        status = "counterexample"
    elif results and all(branch.status == "proved" for branch in results):
        status = "proved"
    else:
        status = "unknown"
    return SymbolicResult(status=status, branches=tuple(results), explored=explored)
