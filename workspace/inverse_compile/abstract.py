"""Abstract Hardy-style counters over Cantor-normal-form digit lists.

A configuration is an argument ``n`` plus digits ``(d0, d1, ..., dk)`` for
``omega^k*dk + ... + omega*d1 + d0``.  A successor step decrements ``d0`` and
increments ``n``.  A limit-style step decrements the lowest nonzero higher
digit ``dj`` and refills ``d(j-1)`` from the current argument.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class CounterConfig:
    n: int
    digits: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.n < 0 or any(digit < 0 for digit in self.digits):
            raise ValueError("counter values must be nonnegative")
        if not self.digits:
            raise ValueError("a counter needs at least one digit")

    @property
    def is_zero(self) -> bool:
        return not any(self.digits)

    @property
    def total(self) -> int:
        return self.n + sum(self.digits)


@dataclass(frozen=True)
class TemplateParams:
    """A sloppy Hardy-counter variant.

    ``refill`` is one of ``n``, ``n+c``, or ``2n+c``.  Keeping the space of
    named expressions tiny makes search results easy to tabulate; richer
    refill operations should be added only after a calibration failure shows
    that they are needed.

    Two champion-inspired variants are also available.  With
    ``successor="double"`` a successor step maps ``n`` to ``2n + c`` instead
    of incrementing it.  With ``consume_refill=True`` a refill step moves
    the accumulator into the refilled digit and resets ``n`` to zero, as in
    the BB(7) champion's rule system, instead of copying ``n`` while
    preserving it.  The consuming variant only retains Hardy-strength growth
    when paired with a growing successor map; on its own with plain
    increments it is just a shuttle.  Its domination lemma is separate work
    and is not claimed by :meth:`dominates_textbook_refill`.
    """

    refill: str = "n"
    refill_const: int = 0
    increment: int = 1
    successor: str = "inc"  # inc or double
    successor_const: int = 2
    consume_refill: bool = False

    def __post_init__(self) -> None:
        if self.refill not in {"n", "n+c", "2n+c"}:
            raise ValueError(f"unknown refill expression: {self.refill!r}")
        if self.increment < 1:
            raise ValueError("the successor increment must be at least one")
        if self.refill_const < 0:
            raise ValueError("refill_const must be nonnegative")
        if self.successor not in {"inc", "double"}:
            raise ValueError(f"unknown successor map: {self.successor!r}")
        if self.successor_const < 0:
            raise ValueError("successor_const must be nonnegative")

    def refill_value(self, n: int) -> int:
        if self.refill == "n":
            return n
        if self.refill == "n+c":
            return n + self.refill_const
        return 2 * n + self.refill_const

    def successor_value(self, n: int) -> int:
        if self.successor == "double":
            return 2 * n + self.successor_const
        return n + self.increment

    def dominates_textbook_refill(self) -> bool:
        """Whether R(n) >= n for all n in this restricted expression family."""
        return True  # n, n+c, and 2n+c with c >= 0 all dominate n.


def step_counter(
    config: CounterConfig, params: TemplateParams = TemplateParams()
) -> CounterConfig | None:
    """Take one abstract step, returning ``None`` at the halting config."""
    digits = list(config.digits)
    if config.is_zero:
        return None
    if digits[0] > 0:
        digits[0] -= 1
        return CounterConfig(params.successor_value(config.n), tuple(digits))
    for index in range(1, len(digits)):
        if digits[index] > 0:
            digits[index] -= 1
            digits[index - 1] = params.refill_value(config.n)
            new_n = 0 if params.consume_refill else config.n
            return CounterConfig(new_n, tuple(digits))
    raise AssertionError("a nonzero config has a nonzero digit")


@dataclass(frozen=True)
class AbstractRun:
    start: CounterConfig
    steps: int
    final: CounterConfig
    halted: bool


def run_counter(
    start: CounterConfig,
    params: TemplateParams = TemplateParams(),
    *,
    max_steps: int = 1_000_000,
    max_value: int = 10_000_000,
) -> AbstractRun:
    config = start
    steps = 0
    while True:
        nxt = step_counter(config, params)
        if nxt is None:
            return AbstractRun(start, steps, config, True)
        config = nxt
        steps += 1
        if config.n > max_value or any(d > max_value for d in config.digits):
            return AbstractRun(start, steps, config, False)
        if steps >= max_steps:
            return AbstractRun(start, steps, config, False)


def trace_counter(
    start: CounterConfig,
    params: TemplateParams = TemplateParams(),
    *,
    max_steps: int = 10_000,
    max_total: int = 10_000,
) -> list[CounterConfig]:
    """Configurations reached from ``start``, including the final zero one."""
    trace = [start]
    config = start
    for _ in range(max_steps):
        nxt = step_counter(config, params)
        if nxt is None:
            break
        if nxt.total > max_total:
            break
        trace.append(nxt)
        config = nxt
    return trace


def initial_config(n: int, n_digits: int, *, top_digit: int = 1) -> CounterConfig:
    if n_digits < 1:
        raise ValueError("n_digits must be positive")
    digits = [0] * n_digits
    digits[-1] = top_digit
    return CounterConfig(n, tuple(digits))


def box_configs(max_n: int, max_digit: int, n_digits: int) -> list[CounterConfig]:
    configs = [
        CounterConfig(n, digits)
        for digits in product(range(max_digit + 1), repeat=n_digits)
        for n in range(max_n + 1)
    ]
    return sorted(configs, key=lambda cfg: (cfg.total, cfg.digits, cfg.n))
