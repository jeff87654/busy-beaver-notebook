"""M2 expressivity pilot: BB(6)/BB(7) champions vs. templates and verifiers.

Run from the workspace root::

    python -m inverse_compile.champions_pilot

The pilot traces both champions from the blank tape to their analysed
checkpoint forms, checks their central rules on constructed tapes with the
literal simulator, and attempts symbolic proofs of the BB(7) rules with
the periodic-pattern verifier.  Verdicts are per rule: proved,
counterexample, or unknown.  Concrete checks are evidence, not proofs.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .abstract import CounterConfig, TemplateParams, initial_config
from .champions import (
    BB6_TEXT,
    BB7_TEXT,
    _step_in_place,
    check_bb6_s1_case,
    check_bb7_b_case,
    trace_bb6_s1_events,
    trace_bb7_b_events,
)
from .engine import synthesize
from .instances import reachable_instances
from .token_encoding import TokenEncoding, b_form_checkpoint_test
from .pattern_symbolic import PatternRule, cells, rep, verify_pattern_rule
from .symbolic import Expr, SymbolicResult
from .tm import HALT, Config, format_table, parse


def _run_low_rule(table, tape: str, expected: str | None, max_steps: int = 60_000):
    config = Config.from_string(tape, head=len(tape), state=0)
    for step in range(1, max_steps + 1):
        status = _step_in_place(table, config)
        if status != "ok":
            return {"status": status, "steps": step, "ok": expected is None and status == "halt"}
        if config.state == 0 and config.ones and config.head == max(config.ones) + 3:
            low = min(config.ones)
            text = "".join(
                "1" if pos in config.ones else "0"
                for pos in range(low, config.head)
            )
            if expected is not None and text == expected:
                return {"status": "a_edge_expected", "steps": step, "ok": True}
    return {"status": "timeout", "steps": max_steps, "ok": False}


def _symbolic_record(name: str, result: SymbolicResult) -> dict:
    return {
        "name": name,
        "status": result.status,
        "explored": result.explored,
        "branches": [asdict(branch) for branch in result.branches],
    }


def _b_items(a_expr: Expr, digit_exponents_near_first: list[Expr]):
    parts = [cells("11")]
    for exponent in reversed(digit_exponents_near_first):
        parts += [cells("1"), rep("01", exponent)]
    parts += [cells("1"), rep("01", a_expr), cells("1"), cells("01"), cells("0011100")]
    return tuple(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("inverse_compile/results/champions_pilot.json"),
    )
    args = parser.parse_args()

    bb7 = parse(BB7_TEXT)
    bb6 = parse(BB6_TEXT)
    payload: dict = {"bb7": {}, "bb6": {}}

    events = trace_bb7_b_events(bb7, max_steps=100_000, max_events=16)
    payload["bb7"]["blank_trace_b_events"] = events
    print(f"BB7 blank trace: {len(events)} B events, first at step {events[0]['step'] if events else None}")

    b_cases = []
    for a in (0, 1, 2, 3, 5):
        for digits in (
            [1], [2], [1, 1], [3, 2], [0, 1], [0, 2],
            [0, 0, 1], [0, 0, 2, 1], [2, 0, 1], [0], [0, 0], [0, 0, 0],
        ):
            b_cases.append(check_bb7_b_case(bb7, a, digits))
    payload["bb7"]["b_rule_concrete_checks"] = b_cases
    print(f"BB7 B-rule concrete checks: {sum(c['ok'] for c in b_cases)}/{len(b_cases)} ok")

    low_rules = []
    for n in range(7):
        record = _run_low_rule(
            bb7, "011" + "01" * n + "0011100", "1" + "01" * (n + 2) + "0011100"
        )
        low_rules.append({"rule": "L1", "n": n, **record})
    for n in range(3):
        record = _run_low_rule(
            bb7,
            "011111" + "01" * n + "0011100",
            "1" + "01" * (n + 5) + "101" + "0011100",
        )
        low_rules.append({"rule": "L2_isolated", "n": n, **record})
    payload["bb7"]["low_rule_concrete_checks"] = low_rules
    print("BB7 low-rule concrete checks recorded (L2/L3 need left context; see README)")

    n = Expr.var("n")
    a = Expr.var("a")
    d = Expr.var("d")
    f = Expr.var("f")
    g = Expr.var("g")
    symbolic_records = []
    symbolic_records.append(
        _symbolic_record(
            "bb7_low_rule_L1",
            verify_pattern_rule(
                bb7,
                PatternRule(
                    "bb7_low_rule_L1",
                    initial=(cells("011"), rep("01", n), cells("0011100")),
                    expected=(cells("1"), rep("01", n + 2), cells("0011100")),
                    assumptions={"n": ("ge", 0)},
                ),
            ),
        )
    )
    symbolic_records.append(
        _symbolic_record(
            "bb7_b_successor",
            verify_pattern_rule(
                bb7,
                PatternRule(
                    "bb7_b_successor",
                    initial=_b_items(a.scale(3), [d.scale(3) + 4, f.scale(3) + 1]),
                    expected=_b_items(
                        (a.scale(2) + 2).scale(3), [d.scale(3) + 1, f.scale(3) + 1]
                    ),
                    assumptions={"a": ("ge", 0), "d": ("ge", 0), "f": ("ge", 0)},
                ),
            ),
        )
    )
    symbolic_records.append(
        _symbolic_record(
            "bb7_b_refill_one_zero",
            verify_pattern_rule(
                bb7,
                PatternRule(
                    "bb7_b_refill_one_zero",
                    initial=_b_items(
                        a.scale(3), [Expr.constant(1), g.scale(3) + 4, f.scale(3) + 1]
                    ),
                    expected=_b_items(
                        Expr.constant(0),
                        [(a.scale(2) + 2).scale(3) + 1, g.scale(3) + 1, f.scale(3) + 1],
                    ),
                    assumptions={"a": ("ge", 0), "g": ("ge", 0), "f": ("ge", 0)},
                ),
            ),
        )
    )
    symbolic_records.append(
        _symbolic_record(
            "bb7_b_halt_all_zero",
            verify_pattern_rule(
                bb7,
                PatternRule(
                    "bb7_b_halt_all_zero",
                    initial=_b_items(a.scale(3), [Expr.constant(1), Expr.constant(1)]),
                    expected=None,
                    assumptions={"a": ("ge", 0)},
                ),
            ),
        )
    )
    # Decomposition of the B successor: one pair-transfer step
    # (u, v) -> (u-1, v+2) on the accumulator suffix, and the finishing
    # phase once the first suffix token is exhausted.
    u = Expr.var("u")
    v = Expr.var("v")

    def suffix_tape(digit_exponents_far_to_near, suffix_pairs):
        parts = [cells("11")]
        for exponent in digit_exponents_far_to_near:
            parts += [cells("1"), rep("01", exponent)]
        for exponent in suffix_pairs:
            parts += [cells("1"), rep("01", exponent)]
        parts += [cells("0011100")]
        return tuple(parts)

    symbolic_records.append(
        _symbolic_record(
            "bb7_pair_transfer_lemma",
            verify_pattern_rule(
                bb7,
                PatternRule(
                    "bb7_pair_transfer_lemma",
                    initial=suffix_tape(
                        [f.scale(3) + 1, d.scale(3) + 4], [u, v]
                    ),
                    expected=suffix_tape(
                        [f.scale(3) + 1, d.scale(3) + 4], [u - 1, v + 2]
                    ),
                    assumptions={
                        "u": ("ge", 1),
                        "v": ("ge", 1),
                        "d": ("ge", 0),
                        "f": ("ge", 0),
                    },
                ),
            ),
        )
    )
    symbolic_records.append(
        _symbolic_record(
            "bb7_successor_finish_phase",
            verify_pattern_rule(
                bb7,
                PatternRule(
                    "bb7_successor_finish_phase",
                    initial=suffix_tape(
                        [f.scale(3) + 1, d.scale(3) + 4],
                        [Expr.constant(0), v],
                    ),
                    expected=suffix_tape(
                        [f.scale(3) + 1, d.scale(3) + 1],
                        [v + 5, Expr.constant(1)],
                    ),
                    assumptions={"v": ("ge", 1), "d": ("ge", 0), "f": ("ge", 0)},
                ),
            ),
        )
    )
    payload["bb7"]["symbolic"] = symbolic_records
    for record in symbolic_records:
        print(f"BB7 symbolic {record['name']}: {record['status']}")

    # Token-encoding synthesis: the champion must pass its own abstract
    # instances (with a B-form checkpoint predicate), and Engine A gets a
    # bounded attempt to rediscover a 7-state machine in this encoding.
    token_params = TemplateParams(
        refill="2n+c",
        refill_const=2,
        successor="double",
        successor_const=2,
        consume_refill=True,
    )
    token_train = reachable_instances(
        [
            initial_config(0, 2),
            initial_config(1, 2),
            initial_config(2, 2),
            CounterConfig(0, (0, 0)),
            CounterConfig(1, (0, 2)),
        ],
        params=token_params,
        encoding=TokenEncoding(),
        max_total=25,
        workspace_slack=64,
        checkpoint_test=b_form_checkpoint_test,
    )
    champion_checks = []
    for instance in token_train:
        evaluation = instance.evaluate(bb7)
        champion_checks.append(
            {
                "instance": instance.name,
                "status": evaluation.status,
                "outcome": evaluation.outcome.status,
                "steps": evaluation.outcome.steps,
            }
        )
    subset = sorted(token_train, key=lambda inst: inst.source.total)[:7]
    synth = synthesize(subset, n_states=7, node_budget=60_000, time_budget_s=90.0)
    payload["bb7"]["token_encoding"] = {
        "champion_self_checks": champion_checks,
        "engine_a_attempt": {
            "n_states": 7,
            "instances": [inst.name for inst in subset],
            "status": synth.status,
            "table": format_table(synth.table) if synth.table else None,
            "stats": asdict(synth.stats),
        },
    }
    passed = sum(c["status"] == "pass" for c in champion_checks)
    print(f"BB7 token champion self-checks: {passed}/{len(champion_checks)} pass")
    print(f"BB7 token Engine A attempt (7 states): {synth.status}")

    s1_events = trace_bb6_s1_events(bb6, max_steps=60_000, max_events=10)
    payload["bb6"]["blank_trace_s1_events"] = s1_events
    print(f"BB6 blank trace S1 events: {s1_events}")

    s1_cases = []
    for m in (2, 1, 0):
        for params in [(2, 1, 0, 0), (2, 2, 1, 1), (3, 3, 2, 2), (3, 5, 3, 3), (2, 1, 4, 4), (3, 7, 0, 5)]:
            s1_cases.append(check_bb6_s1_case(bb6, (params[0], params[1], m, params[2], params[3])))
    for len0, av, bv in [(1, 0, 0), (2, 1, 1), (2, 3, 2), (3, 2, 3), (1, 5, 2)]:
        s1_cases.append(check_bb6_s1_case(bb6, (len0, 0, 0, av, bv)))
        s1_cases.append(check_bb6_s1_case(bb6, (len0, 0, 1, av, bv)))
    payload["bb6"]["s1_rule_concrete_checks"] = s1_cases
    print(f"BB6 S1 concrete checks: {sum(c['ok'] for c in s1_cases)}/{len(s1_cases)} ok")
    payload["bb6"]["symbolic"] = [
        {
            "name": "bb6_s1_inc_rst",
            "status": "unknown",
            "reason": (
                "Inc/Rst outputs contain 2^b run lengths, which are not "
                "affine expressions; the current symbolic verifiers cannot "
                "state, let alone prove, these rules. Concrete checks only."
            ),
        }
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
