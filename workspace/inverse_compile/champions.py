"""Trace and concrete rule checks for the BB(6) and BB(7) champions.

BB(7) champion (Kropitz 2025, analysis by Ligocki on the bbchallenge
wiki).  In the empirical parameterization used here a checkpoint tape is

    11  prod_i [1 (01)^(3 d_i + 1)]  1 (01)^(3A) 1 01 0011100   A>

with digits listed nearest-first as ``d_0, d_1, ...`` (the product runs
from the far digit to the nearest).  The head is in state A on the first
blank cell to the right.  The abstract rules, validated below on the blank
trace and on constructed tapes, are a sloppy Hardy counter:

* successor (``d_0 > 0``): ``d_0 -= 1`` and ``A := 2A + 2``;
* refill (``d_0 = ... = d_{k-1} = 0 < d_k``): ``d_{k-1} := 2A + 2``,
  ``d_k -= 1`` and ``A := 0`` (the accumulator is consumed, not copied);
* halt when every digit is zero.

BB(6) champion (mxdys 2025, analysis on the wiki).  Its S1 configurations
are ``LH LC(len0, a0) 100 10 1^(m+3a) 0 11100 1^(3(1+b))`` with
``LH = 111011`` and the head in state E on the last cell of the
``1^(m+3a)`` run.  ``LC`` encodes a value in 3-cell blocks (100 = bit 1,
111 = bit 0, most significant first).  The Inc/Rst rules are implemented
in :func:`bb6_s1_next`; they involve ``2^b`` terms, so they are outside
the affine symbolic verifier's expression language.
"""
from __future__ import annotations

import re

from .tm import HALT, Config, Table, parse

BB7_TEXT = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF"
BB6_TEXT = "1RB1RA_1RC1RZ_1LD0RF_1RA0LE_0LD1RC_1RA0RE"

BB6_S1_START_STEP = 27_965
BB7_B_START_STEP = 8_178


def _step_in_place(table: Table, config: Config) -> str:
    entry = table[config.state][config.read()]
    if entry is None:
        return "undef"
    write, direction, next_state = entry
    if write:
        config.ones.add(config.head)
    else:
        config.ones.discard(config.head)
    config.head += direction
    config.state = next_state
    return "halt" if next_state == HALT else "ok"


def _tape_left_of_head(config: Config) -> str:
    if not config.ones:
        return ""
    low = min(config.ones)
    return "".join(
        "1" if pos in config.ones else "0" for pos in range(low, config.head)
    )


# ---------------------------------------------------------------------------
# BB(7): B-form tapes, parsing, rules, tracing
# ---------------------------------------------------------------------------

_BB7_GENERAL = re.compile(r"11((?:1(?:01)*)*)0011100")


def bb7_b_tape(a: int, digits_near_first: list[int]) -> str:
    """The finite tape (left of the head) of a B-form configuration."""
    text = "11"
    for digit in reversed(digits_near_first):
        text += "1" + "01" * (3 * digit + 1)
    text += "1" + "01" * (3 * a) + "1" + "01" + "0011100"
    return text


def bb7_b_config(a: int, digits_near_first: list[int]) -> Config:
    tape = bb7_b_tape(a, digits_near_first)
    return Config.from_string(tape, head=len(tape), state=0)


def parse_bb7_b(config: Config) -> tuple[int, list[int]] | None:
    """Parse ``(A, digits near-first)`` if ``config`` is exactly B-form."""
    if config.state != 0 or not config.ones:
        return None
    if config.head != max(config.ones) + 3:
        return None
    text = _tape_left_of_head(config)
    match = _BB7_GENERAL.fullmatch(text)
    if not match:
        return None
    middle = match.group(1)
    blocks: list[int] = []
    index = 0
    while index < len(middle):
        if middle[index] != "1":
            return None
        index += 1
        count = 0
        while middle[index : index + 2] == "01":
            count += 1
            index += 2
        blocks.append(count)
    if len(blocks) < 3 or blocks[-1] != 1 or blocks[-2] % 3:
        return None
    digit_blocks = blocks[:-2]
    if any((block - 1) % 3 for block in digit_blocks):
        return None
    a = blocks[-2] // 3
    digits = list(reversed([(block - 1) // 3 for block in digit_blocks]))
    if bb7_b_tape(a, digits) != text:
        return None
    return a, digits


def bb7_b_next(a: int, digits_near_first: list[int]) -> tuple[str, int, list[int]]:
    """One abstract B step: ``(kind, new A, new digits)``."""
    digits = list(digits_near_first)
    if not any(digits):
        return "halt", a, digits
    if digits[0] > 0:
        digits[0] -= 1
        return "succ", 2 * a + 2, digits
    index = 0
    while digits[index] == 0:
        index += 1
    digits[index - 1] = 2 * a + 2
    digits[index] -= 1
    return "refill", 0, digits


def _run_until_bb7_b(table: Table, config: Config, max_steps: int):
    for step in range(1, max_steps + 1):
        status = _step_in_place(table, config)
        if status != "ok":
            return status, step, None
        parsed = parse_bb7_b(config)
        if parsed is not None:
            return "b_form", step, parsed
    return "timeout", max_steps, None


def check_bb7_b_case(
    table: Table, a: int, digits_near_first: list[int], *, max_steps: int = 2_000_000
) -> dict:
    kind, expected_a, expected_digits = bb7_b_next(a, digits_near_first)
    status, steps, parsed = _run_until_bb7_b(
        table, bb7_b_config(a, digits_near_first), max_steps
    )
    if kind == "halt":
        ok = status == "halt"
    else:
        ok = status == "b_form" and parsed == (expected_a, expected_digits)
    return {
        "a": a,
        "digits": list(digits_near_first),
        "kind": kind,
        "status": status,
        "steps": steps,
        "expected": None if kind == "halt" else [expected_a, expected_digits],
        "actual": None if parsed is None else [parsed[0], parsed[1]],
        "ok": ok,
    }


def trace_bb7_b_events(
    table: Table, *, max_steps: int = 1_000_000, max_events: int = 8
) -> list[dict]:
    """B-form events in the blank-tape run, with rule-consistency flags."""
    config = Config()
    events: list[dict] = []
    step = 0
    while step < max_steps and len(events) < max_events:
        status, used, parsed = _run_until_bb7_b(table, config, max_steps - step)
        step += used
        if status != "b_form" or parsed is None:
            break
        a, digits = parsed
        follows_rule = None
        if events:
            prev = events[-1]
            kind, exp_a, exp_digits = bb7_b_next(prev["a"], prev["digits"])
            follows_rule = (kind != "halt" and (a, digits) == (exp_a, exp_digits))
        events.append(
            {"step": step, "a": a, "digits": digits, "follows_rule": follows_rule}
        )
    return events


# ---------------------------------------------------------------------------
# BB(6): S1 configurations, parsing, rules, tracing
# ---------------------------------------------------------------------------

BB6_LH = "111011"
BB6_S1_STATE = 4  # state E


def lc_encode(length: int, value: int) -> str:
    """mxdys's LC encoding: 3-cell blocks, 100 = bit 1, 111 = bit 0."""
    if length == 0:
        if value != 0:
            raise ValueError("LC(0, x) requires x == 0")
        return ""
    if not (0 <= value < 2**length):
        raise ValueError("value does not fit in the given LC length")
    return lc_encode(length - 1, value // 2) + ("100" if value & 1 else "111")


def bb6_s1_tape(len0: int, a0: int, m: int, a: int, b: int) -> str:
    return (
        BB6_LH
        + lc_encode(len0, a0)
        + "100"
        + "10"
        + "1" * (m + 3 * a)
        + "0"
        + "11100"
        + "1" * (3 * (1 + b))
    )


def bb6_s1_config(len0: int, a0: int, m: int, a: int, b: int) -> Config:
    tape = bb6_s1_tape(len0, a0, m, a, b)
    head = len(BB6_LH + lc_encode(len0, a0) + "100" + "10" + "1" * (m + 3 * a)) - 1
    return Config.from_string(tape, head=head, state=BB6_S1_STATE)


def parse_bb6_s1(config: Config) -> tuple[int, int, int, int, int] | None:
    """Parse ``(len0, a0, m, a, b)`` if ``config`` is exactly S1-form."""
    if config.state != BB6_S1_STATE or not config.ones:
        return None
    low, high = min(config.ones), max(config.ones)
    text = "".join("1" if pos in config.ones else "0" for pos in range(low, high + 1))
    if not text.startswith(BB6_LH):
        return None
    rest = text[len(BB6_LH) :]
    head_rel = config.head - low
    index = len(rest)
    final_run = 0
    while index > 0 and rest[index - 1] == "1":
        index -= 1
        final_run += 1
    if final_run == 0 or final_run % 3:
        return None
    b = final_run // 3 - 1
    if rest[index - 5 : index] != "11100":
        return None
    index -= 5
    if rest[index - 1] != "0":
        return None
    index -= 1
    if head_rel != len(BB6_LH) + index - 1:
        return None
    run = 0
    cursor = index
    while cursor > 0 and rest[cursor - 1] == "1":
        cursor -= 1
        run += 1
    m, a = run % 3, run // 3
    if rest[cursor - 2 : cursor] != "10":
        return None
    cursor -= 2
    if rest[cursor - 3 : cursor] != "100":
        return None
    cursor -= 3
    if cursor % 3:
        return None
    len0 = cursor // 3
    a0 = 0
    for block in range(len0):
        triple = rest[3 * block : 3 * block + 3]
        if triple == "100":
            a0 = 2 * a0 + 1
        elif triple == "111":
            a0 = 2 * a0
        else:
            return None
    if bb6_s1_tape(len0, a0, m, a, b) != text:
        return None
    return len0, a0, m, a, b


def bb6_s1_next(params: tuple[int, int, int, int, int]):
    """One Inc/Rst step: ``(kind, next params or None for halt)``."""
    len0, a0, m, a, b = params
    if a0 > 0:
        if m == 2:
            return "Inc2", (len0, a0 - 1, 1, a + b + 2, 2**b - 1)
        if m == 1:
            return "Inc1", (len0, a0 - 1, 0, a + b + 2, 2**b - 1)
        return "Inc0", (len0, a0 - 1, 2, a + b + 1, 2**b - 1)
    if m == 0:
        return "Rst0", None
    if m == 1:
        return "Rst1", (
            len0 + a + 2,
            2 ** (len0 + a + 2) - 2**a - 1,
            2,
            b,
            2**b - 1,
        )
    return "unknown", None


def _run_until_bb6_s1(table: Table, config: Config, max_steps: int):
    for step in range(1, max_steps + 1):
        status = _step_in_place(table, config)
        if status != "ok":
            return status, step, None
        parsed = parse_bb6_s1(config)
        if parsed is not None:
            return "s1_form", step, parsed
    return "timeout", max_steps, None


def check_bb6_s1_case(
    table: Table,
    params: tuple[int, int, int, int, int],
    *,
    max_steps: int = 5_000_000,
) -> dict:
    kind, expected = bb6_s1_next(params)
    status, steps, parsed = _run_until_bb6_s1(
        table, bb6_s1_config(*params), max_steps
    )
    if kind == "Rst0":
        ok = status == "halt"
    else:
        ok = status == "s1_form" and parsed == expected
    return {
        "params": list(params),
        "kind": kind,
        "status": status,
        "steps": steps,
        "expected": None if expected is None else list(expected),
        "actual": None if parsed is None else list(parsed),
        "ok": ok,
    }


def find_bb6_s1_start(
    table: Table, *, max_steps: int = 200_000
) -> tuple[int, tuple[int, int, int, int, int]] | None:
    """First S1-form configuration in the blank-tape run and its step."""
    config = Config()
    for step in range(1, max_steps + 1):
        if _step_in_place(table, config) != "ok":
            return None
        parsed = parse_bb6_s1(config)
        if parsed is not None:
            return step, parsed
    return None


def trace_bb6_s1_events(
    table: Table, *, max_steps: int = 60_000, max_events: int = 10
) -> list[dict]:
    """Every S1-form configuration in the blank run up to the step bound.

    The blank run reaches a degenerate S1 form early and the analysed
    start ``S1(3, 7, 2, 6, 63)`` at step 27,965; no other S1 form occurs
    in between, so the start-up itself is not an Inc/Rst iteration.
    """
    config = Config()
    events: list[dict] = []
    for step in range(1, max_steps + 1):
        if _step_in_place(table, config) != "ok":
            break
        parsed = parse_bb6_s1(config)
        if parsed is not None:
            events.append({"step": step, "params": list(parsed)})
            if len(events) >= max_events:
                break
    return events
