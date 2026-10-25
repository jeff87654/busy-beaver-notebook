"""Iterate a proved one-step simulation into a whole-run certificate.

If the symbolic verifier has proved one abstract step for every counter
configuration at a fixed digit length, then by induction the machine,
started from any encoded configuration, follows the abstract trace
checkpoint by checkpoint until the abstract program halts.  This module
composes that induction for a concrete start: it walks the abstract
trace, simulates each concrete leg end-to-end (feeding each checkpoint
configuration into the next leg), checks the decoded result against the
abstract successor, and totals the exact step count.  The symbolic proof
is the guarantee that no leg can deviate; the concrete walk is an
independent cross-check and gives exact totals for the chosen start.

A universal lower bound needs no simulation at all: every abstract step
and the final halt cost at least one machine step each.
"""
from __future__ import annotations

from dataclasses import dataclass

from .abstract import CounterConfig, TemplateParams, run_counter, step_counter
from .encoding import BlockEncoding
from .symbolic import SymbolicResult
from .tm import Table, run_until


@dataclass(frozen=True)
class CertifiedRun:
    start: CounterConfig
    abstract_steps: int
    tm_steps: int
    lower_bound_steps: int
    final: CounterConfig
    halted: bool


def abstract_lower_bound(
    start: CounterConfig,
    params: TemplateParams = TemplateParams(),
    *,
    max_steps: int = 1_000_000,
    max_value: int = 10_000_000,
) -> int | None:
    """Machine-step lower bound from the abstract trace length, if it halts."""
    run = run_counter(start, params, max_steps=max_steps, max_value=max_value)
    if not run.halted:
        return None
    return run.steps + 1  # one step per abstract leg plus the halt leg


def certified_run(
    table: Table,
    *,
    start: CounterConfig,
    symbolic_result: SymbolicResult,
    params: TemplateParams = TemplateParams(),
    encoding: BlockEncoding = BlockEncoding(),
    phase_state: int = 0,
    max_abstract_steps: int = 100_000,
    max_leg_steps: int = 1_000_000,
) -> CertifiedRun:
    """Compose a proved one-step simulation over a whole abstract run.

    Raises ``ValueError`` if the symbolic result is not a proof, and
    ``AssertionError`` if a concrete leg disagrees with the abstract
    successor (which would refute the symbolic proof for this encoding).
    """
    if not symbolic_result.proved:
        raise ValueError("certification requires a proved one-step simulation")
    n_digits = len(start.digits)
    abstract = start
    tm_config = encoding.encode(start, phase_state=phase_state)
    total_steps = 0
    abstract_steps = 0
    while True:
        if abstract_steps > max_abstract_steps:
            raise AssertionError("abstract run exceeds the certification bound")
        nxt = step_counter(abstract, params)
        outcome = run_until(
            table,
            tm_config,
            checkpoint_state=phase_state,
            max_steps=max_leg_steps,
            max_span=1_000_000,
        )
        total_steps += outcome.steps
        if nxt is None:
            if outcome.status != "halt":
                raise AssertionError(
                    f"expected halt from {abstract}, got {outcome.status}"
                )
            return CertifiedRun(
                start=start,
                abstract_steps=abstract_steps,
                tm_steps=total_steps,
                lower_bound_steps=abstract_steps + 1,
                final=abstract,
                halted=True,
            )
        if outcome.status != "checkpoint":
            raise AssertionError(
                f"expected checkpoint from {abstract}, got {outcome.status}"
            )
        decoded = encoding.decode(outcome.config, n_digits)
        if decoded != nxt:
            raise AssertionError(
                f"checkpoint mismatch from {abstract}: decoded {decoded}, "
                f"abstract successor is {nxt}"
            )
        abstract = nxt
        tm_config = outcome.config
        abstract_steps += 1
