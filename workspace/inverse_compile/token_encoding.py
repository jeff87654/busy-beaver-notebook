"""BB(7)-style ``(01)``-token encoding for abstract counters.

A counter configuration ``(n, (d0, d1, ...))`` is encoded exactly as a
BB(7) B-form tape with accumulator ``A = n`` and digits nearest-first:

    11  prod_i [1 (01)^(3 d_i + 1)]  1 (01)^(3n) 1 01 0011100   A>

Synthesis instances over this encoding must use a checkpoint *predicate*
(the tape parses as a B-form), not merely a checkpoint state, because a
champion-style machine returns to state A at the right edge many times
inside one abstract step.  Use :func:`b_form_checkpoint_test` as the
instances' ``checkpoint_test``.
"""
from __future__ import annotations

from dataclasses import dataclass

from .abstract import CounterConfig
from .champions import bb7_b_config, parse_bb7_b
from .tm import Config


@dataclass(frozen=True)
class TokenEncoding:
    """Encode counters as BB(7) B-form tapes (phase state A only)."""

    def encode(self, config: CounterConfig, *, phase_state: int = 0) -> Config:
        if phase_state != 0:
            raise ValueError("the token encoding's phase state is A (0)")
        return bb7_b_config(config.n, list(config.digits))

    def decode_relative(
        self, relative_ones: frozenset[int], n_digits: int
    ) -> CounterConfig:
        if not relative_ones:
            raise ValueError("a B-form tape is never blank")
        low = min(relative_ones)
        shifted = Config(
            ones={pos - low for pos in relative_ones}, head=-low, state=0
        )
        parsed = parse_bb7_b(shifted)
        if parsed is None:
            raise ValueError("tape does not parse as a B-form")
        a, digits = parsed
        if len(digits) != n_digits:
            raise ValueError(
                f"expected {n_digits} digits, parsed {len(digits)}"
            )
        return CounterConfig(a, tuple(digits))

    def decode(self, config: Config, n_digits: int) -> CounterConfig:
        return self.decode_relative(config.relative_ones(), n_digits)


def b_form_checkpoint_test(config: Config) -> bool:
    """Accept a checkpoint only when the tape is exactly B-form."""
    return parse_bb7_b(config) is not None
