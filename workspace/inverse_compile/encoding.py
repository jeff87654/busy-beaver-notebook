"""Tape encodings for abstract counter configurations.

The version-0 layout is deliberately plain::

    1^(n+c) 0 1^(d0+c) 0 1^(d1+c) ... 1^(dk+c)

The checkpoint head position is part of the template.  ``left`` puts it on
cell 0.  ``n_right`` puts it on the last cell of the leading ``n`` block (or
on the separator when that block is empty), which makes separator-shifting
counter implementations possible.  Offset ``c >= 1`` keeps zero digits
visible as short blocks.  Offset zero is allowed for one-digit counters,
where a missing trailing block is unambiguous.
"""
from __future__ import annotations

from dataclasses import dataclass

from .abstract import CounterConfig
from .tm import Config


@dataclass(frozen=True)
class BlockEncoding:
    offset: int = 1
    head_anchor: str = "left"  # left or n_right

    def __post_init__(self) -> None:
        if self.offset < 0:
            raise ValueError("offset must be nonnegative")
        if self.head_anchor not in {"left", "n_right"}:
            raise ValueError(f"unknown head anchor: {self.head_anchor!r}")

    def block_length(self, value: int) -> int:
        return value + self.offset

    def encode(self, config: CounterConfig, *, phase_state: int = 0) -> Config:
        n_digits = len(config.digits)
        if n_digits > 1 and self.offset == 0:
            raise ValueError("offset-zero encodings are ambiguous for several digits")
        values = (config.n,) + config.digits
        ones: set[int] = set()
        position = 0
        for block_index, value in enumerate(values):
            length = self.block_length(value)
            ones.update(range(position, position + length))
            position += length
            if block_index != len(values) - 1:
                position += 1  # one zero separator
        if self.head_anchor == "n_right":
            head = max(self.block_length(config.n) - 1, 0)
        else:
            head = 0
        return Config(ones=ones, head=head, state=phase_state)

    @staticmethod
    def _segments(relative_ones: frozenset[int]) -> list[int]:
        if not relative_ones:
            return []
        low, high = min(relative_ones), max(relative_ones)
        if low != 0:
            raise ValueError("encoded tape does not start at the checkpoint head")
        segments: list[int] = []
        current = 0
        zero_run = 0
        for position in range(low, high + 1):
            if position in relative_ones:
                if zero_run:
                    if zero_run != 1:
                        raise ValueError("blocks must be separated by exactly one zero")
                    segments.append(current)
                    current = 0
                    zero_run = 0
                current += 1
            else:
                zero_run += 1
        segments.append(current)
        return segments

    @classmethod
    def _segments_with_leading_zero(cls, relative_ones: frozenset[int]) -> list[int]:
        if min(relative_ones) != 1:
            raise ValueError("a leading empty block needs exactly one separator zero")
        shifted = frozenset(position - 1 for position in relative_ones)
        return [0] + cls._segments(shifted)

    def _normalize_to_origin(
        self, relative_ones: frozenset[int], n_digits: int
    ) -> frozenset[int]:
        """Shift checkpoint-relative positions so the tape origin is zero."""
        if not relative_ones or self.head_anchor == "left":
            return relative_ones
        low = min(relative_ones)
        if self.offset > 0:
            origin = low
        elif n_digits == 1:
            if low < 0:
                origin = low  # leftmost cell of a nonempty n-block
            elif low in {0, 1}:
                origin = 0  # the head is the separator or a one-cell n-block
            else:
                raise ValueError("encoded tape starts too far from the head")
        else:
            raise ValueError("offset-zero encodings are ambiguous for several digits")
        return frozenset(position - origin for position in relative_ones)

    def decode_relative(
        self, relative_ones: frozenset[int], n_digits: int
    ) -> CounterConfig:
        normalized = self._normalize_to_origin(relative_ones, n_digits)
        if self.offset == 0 and n_digits == 1:
            if not normalized:
                return CounterConfig(0, (0,))
            if min(normalized) < 0:
                raise ValueError("encoded tape starts before the tape origin")
            # An empty leading n-block is visible as a separator zero at
            # the origin, so its first 1 is at position one.
            if min(normalized) == 0:
                segments = self._segments(normalized)
            else:
                segments = self._segments_with_leading_zero(normalized)
            if len(segments) == 1:
                return CounterConfig(segments[0], (0,))
            if len(segments) != 2:
                raise ValueError(f"expected two blocks, found {segments}")
            return CounterConfig(segments[0], (segments[1],))
        segments = self._segments(normalized)
        expected = n_digits + 1
        if len(segments) != expected:
            raise ValueError(
                f"expected {expected} blocks, found {len(segments)}: {segments}"
            )
        values = [length - self.offset for length in segments]
        if any(value < 0 for value in values):
            raise ValueError(f"a block is shorter than the offset: {segments}")
        return CounterConfig(values[0], tuple(values[1:]))

    def decode(self, config: Config, n_digits: int) -> CounterConfig:
        """Decode a configuration whose head is at the checkpoint anchor."""
        return self.decode_relative(config.relative_ones(), n_digits)
