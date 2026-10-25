"""Bounded counterexample search.

This module is intentionally *not* the symbolic verifier from the project
spec.  It can refute a candidate on a finite box of counter configurations,
and it distinguishes three outcomes:

* ``counterexample``: a completed run reaches the wrong terminal form;
* ``unknown``: a bound or an unassigned transition prevents a verdict;
* ``pass_bounded``: every configuration in the finite box passes.

``pass_bounded`` must never be reported as a proof for all block lengths.
"""
from __future__ import annotations

from dataclasses import dataclass

from .abstract import CounterConfig, TemplateParams
from .encoding import BlockEncoding
from .instances import Evaluation, Instance, box_instances, step_instance
from .tm import Table


@dataclass(frozen=True)
class VerificationResult:
    status: str  # pass_bounded, counterexample, unknown
    checked: int
    evaluation: Evaluation | None = None

    @property
    def counterexample(self) -> Instance | None:
        if self.status == "counterexample" and self.evaluation is not None:
            return self.evaluation.instance
        return None


def classify_evaluation(evaluation: Evaluation) -> str:
    if evaluation.status == "pass":
        return "pass"
    if evaluation.status == "undef":
        return "unknown"
    if evaluation.outcome.status in {"timeout", "overflow"}:
        return "unknown"
    # A loop verdict is exact for a completed table because the repeated
    # configuration is translation-invariant.  A wrong checkpoint or wrong
    # halt/checkpoint terminal is also a genuine counterexample.
    return "counterexample"


def verify_instances(table: Table, instances: list[Instance]) -> VerificationResult:
    checked = 0
    first_unknown: Evaluation | None = None
    for instance in instances:
        evaluation = instance.evaluate(table)
        checked += 1
        verdict = classify_evaluation(evaluation)
        if verdict == "counterexample":
            return VerificationResult("counterexample", checked, evaluation)
        if verdict == "unknown" and first_unknown is None:
            first_unknown = evaluation
    if first_unknown is not None:
        return VerificationResult("unknown", checked, first_unknown)
    return VerificationResult("pass_bounded", checked)


def verify_box(
    table: Table,
    *,
    max_n: int,
    max_digit: int,
    n_digits: int,
    params: TemplateParams = TemplateParams(),
    encoding: BlockEncoding = BlockEncoding(),
    phase_state: int = 0,
) -> VerificationResult:
    instances = box_instances(
        max_n=max_n,
        max_digit=max_digit,
        n_digits=n_digits,
        params=params,
        encoding=encoding,
        phase_state=phase_state,
    )
    return verify_instances(table, instances)


def verify_one_config(
    table: Table,
    config: CounterConfig,
    *,
    params: TemplateParams = TemplateParams(),
    encoding: BlockEncoding = BlockEncoding(),
    phase_state: int = 0,
) -> VerificationResult:
    instance = step_instance(config, params, encoding, phase_state=phase_state)
    return verify_instances(table, [instance])
