"""Concrete input/output requirements for one abstract transition."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .abstract import (
    CounterConfig,
    TemplateParams,
    box_configs,
    step_counter,
    trace_counter,
)
from .encoding import BlockEncoding
from .tm import Config, RunOutcome, Table, run_until


@dataclass(frozen=True)
class Instance:
    """Run from ``start`` to the first re-entry to ``checkpoint_state``.

    ``expected_ones`` is stored relative to the final head position.  For a
    halting instance it may be ``None``, meaning that any final tape reached
    by an actual halt transition is accepted.
    """

    name: str
    start: Config
    expected_ones: frozenset[int] | None
    expect_halt: bool = False
    checkpoint_state: int = 0
    max_steps: int = 500
    max_span: int = 120
    source: CounterConfig | None = None
    # Optional extra acceptance condition on checkpoint configurations,
    # e.g. "tape parses as a B-form" for champion-style checkpoints where
    # the phase state is visited many times inside one abstract step.
    checkpoint_test: Callable[[Config], bool] | None = field(
        default=None, compare=False, repr=False
    )

    def evaluate(self, table: Table) -> "Evaluation":
        outcome = run_until(
            table,
            self.start,
            checkpoint_state=self.checkpoint_state,
            max_steps=self.max_steps,
            max_span=self.max_span,
            checkpoint_test=self.checkpoint_test,
        )
        if outcome.status == "undef":
            return Evaluation("undef", self, outcome, "undefined transition")
        if self.expect_halt:
            if outcome.status != "halt":
                return Evaluation(
                    "fail", self, outcome, f"expected halt, got {outcome.status}"
                )
            if (
                self.expected_ones is not None
                and outcome.config.relative_ones() != self.expected_ones
            ):
                return Evaluation("fail", self, outcome, "wrong final tape")
            return Evaluation("pass", self, outcome, "halted")
        if outcome.status != "checkpoint":
            return Evaluation(
                "fail", self, outcome, f"expected checkpoint, got {outcome.status}"
            )
        if outcome.config.relative_ones() != self.expected_ones:
            return Evaluation("fail", self, outcome, "wrong checkpoint tape")
        return Evaluation("pass", self, outcome, "checkpoint tape matches")


@dataclass(frozen=True)
class Evaluation:
    status: str  # pass, fail, undef
    instance: Instance
    outcome: RunOutcome
    reason: str

    @property
    def is_pass(self) -> bool:
        return self.status == "pass"


def default_step_budget(config: CounterConfig, encoding: BlockEncoding) -> int:
    """A generous sweep/copy budget for one abstract step at this size."""
    encoded = encoding.encode(config)
    span = encoded.span()
    return 40 + 15 * span + 4 * span * span


def step_instance(
    config: CounterConfig,
    params: TemplateParams,
    encoding,
    *,
    phase_state: int = 0,
    max_steps: int | None = None,
    workspace_slack: int = 8,
    checkpoint_test: Callable[[Config], bool] | None = None,
) -> Instance:
    start = encoding.encode(config, phase_state=phase_state)
    nxt = step_counter(config, params)
    budget = default_step_budget(config, encoding) if max_steps is None else max_steps
    name = f"n={config.n},d={config.digits}"
    if nxt is None:
        return Instance(
            name=name,
            start=start,
            expected_ones=None,
            expect_halt=True,
            checkpoint_state=phase_state,
            max_steps=budget,
            max_span=start.span() + workspace_slack,
            source=config,
            checkpoint_test=checkpoint_test,
        )
    expected = encoding.encode(nxt, phase_state=phase_state)
    return Instance(
        name=name,
        start=start,
        expected_ones=expected.relative_ones(),
        checkpoint_state=phase_state,
        max_steps=budget,
        max_span=max(start.span(), expected.span()) + workspace_slack,
        source=config,
        checkpoint_test=checkpoint_test,
    )


def box_instances(
    *,
    max_n: int,
    max_digit: int,
    n_digits: int,
    params: TemplateParams = TemplateParams(),
    encoding=BlockEncoding(),
    phase_state: int = 0,
    max_steps: int | None = None,
    workspace_slack: int = 8,
    checkpoint_test: Callable[[Config], bool] | None = None,
) -> list[Instance]:
    """Every abstract step in a finite box, smallest configurations first."""
    return [
        step_instance(
            config,
            params,
            encoding,
            phase_state=phase_state,
            max_steps=max_steps,
            workspace_slack=workspace_slack,
            checkpoint_test=checkpoint_test,
        )
        for config in box_configs(max_n, max_digit, n_digits)
    ]


def reachable_instances(
    starts: list[CounterConfig],
    *,
    params: TemplateParams = TemplateParams(),
    encoding=BlockEncoding(),
    phase_state: int = 0,
    max_abstract_steps: int = 10_000,
    max_total: int = 1_000,
    max_steps: int | None = None,
    workspace_slack: int = 8,
    checkpoint_test: Callable[[Config], bool] | None = None,
) -> list[Instance]:
    """One instance per distinct configuration reachable from ``starts``.

    This implements the partial-specification choice: a candidate need only
    be correct on configurations that the abstract program actually reaches
    from the chosen seeds, not on the entire box.
    """
    seen: dict[CounterConfig, None] = {}
    for start in starts:
        for config in trace_counter(
            start, params, max_steps=max_abstract_steps, max_total=max_total
        ):
            seen.setdefault(config)
    configs = sorted(seen, key=lambda cfg: (cfg.total, cfg.digits, cfg.n))
    return [
        step_instance(
            config,
            params,
            encoding,
            phase_state=phase_state,
            max_steps=max_steps,
            workspace_slack=workspace_slack,
            checkpoint_test=checkpoint_test,
        )
        for config in configs
    ]
