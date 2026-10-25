"""Growth facts for the consuming/doubling counter variant.

The exact digit-clearing lemma is elementary: iterating the successor
map ``A := 2A + c`` exactly ``v`` times (one per unit of ``d0``) gives
``A_v = 2^v * A_0 + c (2^v - 1)``.  This module implements that closed
form and checks two domination statements on finite sample grids
against the textbook Hardy counter (same digit list, same start):

* final accumulator: consuming/doubling finishes with at least the
  textbook final ``n``;
* abstract step count: consuming/doubling takes at least as many
  abstract steps.

The phase-coupling argument for a general domination proof goes by
induction on the lowest nonzero digit position: within one phase both
systems decrement the same digit, the consuming refill value ``2n + 2``
is at least the textbook refill ``n`` whenever the consuming accumulator
is at least the textbook one at phase start, and clearing the larger
refilled digit restores accumulator dominance by the clearing lemma
(the reset to zero is more than repaid by doubling).  Turning that
sketch into a checked induction over digit lists is still open work;
the sample checks here are evidence, not that proof.
"""
from __future__ import annotations

from itertools import product

from .abstract import CounterConfig, TemplateParams, run_counter

CONSUMING_DOUBLING = TemplateParams(
    refill="2n+c",
    refill_const=2,
    successor="double",
    successor_const=2,
    consume_refill=True,
)
TEXTBOOK = TemplateParams()


def clear_digit_final_a(a0: int, v: int, c: int = 2) -> int:
    """Accumulator after clearing a digit of value ``v`` by successors."""
    return (2**v) * a0 + c * (2**v - 1)


def domination_samples(
    *,
    max_n: int = 2,
    max_digit: int = 3,
    n_digits: int = 3,
    value_cap: int = 10**18,
) -> dict:
    """Compare both systems on a finite grid of starts.

    A run that exceeds ``value_cap`` counts as exceeding any finished
    value on that side; if both sides exceed the cap the comparison for
    that start is recorded as undecided rather than a domination proof.
    """
    checked = 0
    undecided = 0
    final_dominated = 0
    steps_dominated = 0
    failures: list[dict] = []
    for digits in product(range(max_digit + 1), repeat=n_digits):
        for n in range(max_n + 1):
            start = CounterConfig(n, digits)
            consuming = run_counter(
                start, CONSUMING_DOUBLING, max_steps=10_000_000, max_value=value_cap
            )
            textbook = run_counter(
                start, TEXTBOOK, max_steps=10_000_000, max_value=value_cap
            )
            checked += 1
            if not consuming.halted and not textbook.halted:
                undecided += 1
                continue
            consuming_final = consuming.final.n if consuming.halted else value_cap + 1
            textbook_final = textbook.final.n if textbook.halted else value_cap + 1
            consuming_steps = consuming.steps if consuming.halted else 10**18
            textbook_steps = textbook.steps if textbook.halted else 10**18
            final_ok = consuming_final >= textbook_final
            steps_ok = consuming_steps >= textbook_steps
            final_dominated += int(final_ok)
            steps_dominated += int(steps_ok)
            if not (final_ok and steps_ok):
                failures.append(
                    {
                        "start": [n, list(digits)],
                        "consuming_final": consuming_final,
                        "textbook_final": textbook_final,
                        "consuming_steps": consuming_steps,
                        "textbook_steps": textbook_steps,
                    }
                )
    return {
        "checked": checked,
        "undecided": undecided,
        "final_dominated": final_dominated,
        "steps_dominated": steps_dominated,
        "failures": failures,
    }
