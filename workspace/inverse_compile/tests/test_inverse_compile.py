from __future__ import annotations

import unittest

from inverse_compile.abstract import (
    CounterConfig,
    TemplateParams,
    initial_config,
    run_counter,
    step_counter,
)
from inverse_compile.champions import (
    BB6_TEXT,
    BB7_TEXT,
    bb6_s1_config,
    check_bb6_s1_case,
    check_bb7_b_case,
    lc_encode,
    parse_bb6_s1,
    trace_bb6_s1_events,
    trace_bb7_b_events,
)
from inverse_compile.encoding import BlockEncoding
from inverse_compile.engine import synthesize
from inverse_compile.certify import abstract_lower_bound, certified_run
from inverse_compile.growth import clear_digit_final_a, domination_samples
from inverse_compile.instances import Instance, reachable_instances
from inverse_compile.token_encoding import TokenEncoding, b_form_checkpoint_test
from inverse_compile.pattern_symbolic import PatternRule, cells, rep, verify_pattern_rule
from inverse_compile.sat_engine import synthesize_sat
from inverse_compile.sketches import successor_sketch
from inverse_compile.symbolic import Expr, verify_counter_step_symbolic
from inverse_compile.tm import Config, format_table, parse, run_from_blank, run_until
from inverse_compile.verify import verify_box, verify_one_config


class AbstractCounterTests(unittest.TestCase):
    def test_successor_and_limit_steps(self) -> None:
        self.assertEqual(
            step_counter(CounterConfig(5, (2, 0))), CounterConfig(6, (1, 0))
        )
        self.assertEqual(
            step_counter(CounterConfig(5, (0, 2))), CounterConfig(5, (5, 1))
        )
        self.assertIsNone(step_counter(CounterConfig(5, (0, 0))))

    def test_doubling_consuming_variant_steps(self) -> None:
        params = TemplateParams(
            refill="2n+c",
            refill_const=2,
            successor="double",
            successor_const=2,
            consume_refill=True,
        )
        self.assertEqual(
            step_counter(CounterConfig(5, (2, 0)), params),
            CounterConfig(12, (1, 0)),
        )
        self.assertEqual(
            step_counter(CounterConfig(5, (0, 2)), params),
            CounterConfig(0, (12, 1)),
        )

    def test_small_runs(self) -> None:
        two_digit = run_counter(initial_config(2, 2))
        self.assertTrue(two_digit.halted)
        self.assertEqual(two_digit.steps, 3)
        self.assertEqual(two_digit.final, CounterConfig(4, (0, 0)))

        three_digit = run_counter(initial_config(2, 3))
        self.assertTrue(three_digit.halted)
        self.assertEqual(three_digit.steps, 9)
        self.assertEqual(three_digit.final, CounterConfig(8, (0, 0, 0)))


class EncodingTests(unittest.TestCase):
    def test_round_trips(self) -> None:
        cases = [
            (BlockEncoding(1), CounterConfig(0, (0, 0))),
            (BlockEncoding(1), CounterConfig(3, (0, 2, 1))),
            (BlockEncoding(1), CounterConfig(4, (5,))),
            (BlockEncoding(0), CounterConfig(0, (0,))),
            (BlockEncoding(0), CounterConfig(0, (3,))),
            (BlockEncoding(0), CounterConfig(4, (0,))),
            (BlockEncoding(0), CounterConfig(4, (2,))),
            (BlockEncoding(1, "n_right"), CounterConfig(0, (0, 2))),
            (BlockEncoding(1, "n_right"), CounterConfig(3, (4,))),
            (BlockEncoding(0, "n_right"), CounterConfig(0, (3,))),
            (BlockEncoding(0, "n_right"), CounterConfig(1, (0,))),
            (BlockEncoding(0, "n_right"), CounterConfig(4, (2,))),
        ]
        for encoding, config in cases:
            with self.subTest(encoding=encoding, config=config):
                encoded = encoding.encode(config)
                self.assertEqual(
                    encoding.decode_relative(
                        encoded.relative_ones(), len(config.digits)
                    ),
                    config,
                )


class TuringMachineTests(unittest.TestCase):
    def test_parse_format_round_trip(self) -> None:
        for text in (
            "1RB1LB_1LA1RZ",
            "1RB1RZ_1LB0RC_1LC1LA",
            "1RB---_---1RZ",
        ):
            with self.subTest(text=text):
                self.assertEqual(format_table(parse(text)), text)

    def test_literal_simulator_against_known_champions(self) -> None:
        known = [
            ("1RB1LB_1LA1RZ", 6, 4),
            ("1RB1RZ_1LB0RC_1LC1LA", 21, 5),
            ("1RB1LB_1LA0LC_1RZ1LD_1RD0RA", 107, 13),
        ]
        for text, steps, ones in known:
            with self.subTest(text=text):
                outcome = run_from_blank(parse(text), max_steps=1_000)
                self.assertEqual(outcome.status, "halt")
                self.assertEqual(outcome.steps, steps)
                self.assertEqual(len(outcome.config.ones), ones)

    def test_translation_loop_is_detected(self) -> None:
        outcome = run_until(parse("0RA0RA"), Config(), max_steps=100)
        self.assertEqual(outcome.status, "loop")
        self.assertEqual(outcome.steps, 1)


class SynthesisAndVerificationTests(unittest.TestCase):
    def test_engine_can_synthesize_a_halt_transition(self) -> None:
        instance = Instance(
            name="halt-on-blank",
            start=Config(),
            expected_ones=None,
            expect_halt=True,
            max_steps=20,
            max_span=10,
        )
        result = synthesize(
            [instance], n_states=1, node_budget=100, time_budget_s=5.0
        )
        self.assertTrue(result.found, result)
        self.assertIsNotNone(result.table)
        self.assertEqual(result.table[0][0][2], -1)  # type: ignore[index]

    def test_bounded_verifier_distinguishes_counterexample(self) -> None:
        always_halt = parse("1RZ1RZ")
        zero = verify_one_config(always_halt, CounterConfig(0, (0,)))
        self.assertEqual(zero.status, "pass_bounded")

        successor = verify_one_config(always_halt, CounterConfig(0, (1,)))
        self.assertEqual(successor.status, "counterexample")


class DiscoveredCalibrationTests(unittest.TestCase):
    """Behavioral checks for the first machines returned by Engine A.

    The tables are fixtures here; the assertions use the abstract spec and a
    finite box, not the search result that originally produced them.
    """

    def test_one_digit_candidates_pass_their_finite_boxes(self) -> None:
        cases = [
            (
                BlockEncoding(0, "n_right"),
                "0RB1RB_1RC1LB_0RZ0LA",
            ),
            (
                BlockEncoding(1, "n_right"),
                "---1RB_0RB1RC_1RD1LC_0RZ0LA",
            ),
        ]
        for encoding, text in cases:
            with self.subTest(encoding=encoding, text=text):
                result = verify_box(
                    parse(text),
                    max_n=8,
                    max_digit=8,
                    n_digits=1,
                    encoding=encoding,
                )
                self.assertEqual(result.status, "pass_bounded")
                self.assertEqual(result.checked, 81)

    def test_offset_zero_candidate_runs_a_whole_counter_to_halt(self) -> None:
        encoding = BlockEncoding(0, "n_right")
        table = parse("0RB1RB_1RC1LB_0RZ0LA")
        abstract = CounterConfig(0, (5,))
        tm_config = encoding.encode(abstract)
        for _ in range(20):
            nxt = step_counter(abstract)
            outcome = run_until(
                table, tm_config, checkpoint_state=0, max_steps=100, max_span=30
            )
            if nxt is None:
                self.assertEqual(outcome.status, "halt")
                break
            self.assertEqual(outcome.status, "checkpoint")
            self.assertEqual(encoding.decode(outcome.config, 1), nxt)
            abstract = nxt
            tm_config = outcome.config
        else:
            self.fail("counter did not halt within twenty abstract steps")
        self.assertEqual(abstract, CounterConfig(5, (0,)))

    def test_successor_sketch_only_leaves_the_refill_case_open(self) -> None:
        encoding = BlockEncoding(1, "n_right")
        sketch = successor_sketch(6)
        for config in (
            CounterConfig(0, (1, 0)),
            CounterConfig(2, (2, 3)),
            CounterConfig(4, (3, 0)),
        ):
            with self.subTest(config=config):
                result = verify_one_config(sketch, config, encoding=encoding)
                self.assertEqual(result.status, "pass_bounded")
        refill = verify_one_config(
            sketch, CounterConfig(2, (0, 1)), encoding=encoding
        )
        self.assertEqual(refill.status, "unknown")
        self.assertEqual(refill.evaluation.outcome.undef, (2, 0))  # type: ignore[union-attr]


class SymbolicVerifierTests(unittest.TestCase):
    def test_discovered_one_digit_candidates_are_proved_for_all_values(self) -> None:
        cases = [
            (
                BlockEncoding(0, "n_right"),
                "0RB1RB_1RC1LB_0RZ0LA",
            ),
            (
                BlockEncoding(1, "n_right"),
                "---1RB_0RB1RC_1RD1LC_0RZ0LA",
            ),
        ]
        for encoding, text in cases:
            with self.subTest(encoding=encoding, text=text):
                result = verify_counter_step_symbolic(
                    parse(text), n_digits=1, encoding=encoding
                )
                self.assertEqual(result.status, "proved", result.branches)
                self.assertTrue(result.branches)
                self.assertTrue(
                    all(branch.status == "proved" for branch in result.branches)
                )

    def test_variable_length_sweeps_are_proved_as_shift_rules(self) -> None:
        # Hand-built left-anchor transfer machine.  State B sweeps right
        # over the whole n block and D sweeps back left, so the generic
        # successor branch must use a 2*n+4 shift rule rather than only
        # fixed-size cases.
        result = verify_counter_step_symbolic(
            parse("1RC1RB_1RC1RB_0RZ0LD_0RA1LD"),
            n_digits=1,
            encoding=BlockEncoding(0, "left"),
        )
        self.assertEqual(result.status, "proved", result.branches)
        self.assertTrue(
            any(branch.steps == "2*n+4" for branch in result.branches)
        )

    def test_symbolic_verifier_rejects_wrong_and_prematurely_halting_tables(
        self,
    ) -> None:
        encoding = BlockEncoding(1, "n_right")
        premature_halt = verify_counter_step_symbolic(
            parse("1RZ1RZ"), n_digits=1, encoding=encoding
        )
        self.assertEqual(premature_halt.status, "counterexample")

        # The discovered offset-one machine with D1 changed from 0LA to
        # 1LA returns to the checkpoint without shortening d0.
        wrong_tape = verify_counter_step_symbolic(
            parse("---1RB_0RB1RC_1RD1LC_0RZ1LA"),
            n_digits=1,
            encoding=encoding,
        )
        self.assertEqual(wrong_tape.status, "counterexample")
        self.assertTrue(
            any(
                "wrong checkpoint tape" in branch.reason
                for branch in wrong_tape.branches
            )
        )

    def test_successor_sketch_is_proved_and_refill_remains_unknown(self) -> None:
        result = verify_counter_step_symbolic(
            successor_sketch(6),
            n_digits=2,
            encoding=BlockEncoding(1, "n_right"),
        )
        self.assertEqual(result.status, "unknown")
        grouped = result.by_case()
        self.assertTrue(grouped["successor_d0"])
        self.assertTrue(
            all(
                branch.status == "proved"
                for branch in grouped["successor_d0"]
            )
        )
        for case_name in ("refill_from_d1", "halt_all_zero"):
            with self.subTest(case_name=case_name):
                self.assertTrue(
                    all(
                        branch.status == "unknown"
                        and "C0" in branch.reason
                        for branch in grouped[case_name]
                    )
                )


class ChampionTests(unittest.TestCase):
    def test_bb7_blank_trace_reaches_analysed_b_start_by_rules(self) -> None:
        events = trace_bb7_b_events(
            parse(BB7_TEXT), max_steps=100_000, max_events=16
        )
        self.assertTrue(events)
        by_step = {event["step"]: event for event in events}
        self.assertIn(8178, by_step)
        self.assertEqual(by_step[8178]["a"], 2)
        self.assertEqual(by_step[8178]["digits"], [1] * 12)
        self.assertTrue(
            all(event["follows_rule"] for event in events[1:]),
            events,
        )

    def test_bb7_b_rules_on_constructed_tapes(self) -> None:
        table = parse(BB7_TEXT)
        for a, digits in [(2, [1, 1]), (2, [0, 1]), (1, [0, 0, 2, 1]), (3, [0, 0])]:
            with self.subTest(a=a, digits=digits):
                result = check_bb7_b_case(table, a, digits)
                self.assertTrue(result["ok"], result)

    def test_bb6_lc_and_s1_round_trip(self) -> None:
        self.assertEqual(lc_encode(3, 6), "100100111")
        self.assertEqual(lc_encode(3, 7), "100100100")
        params = (3, 7, 2, 6, 63)
        self.assertEqual(parse_bb6_s1(bb6_s1_config(*params)), params)

    def test_bb6_blank_trace_reaches_analysed_s1_start(self) -> None:
        events = trace_bb6_s1_events(parse(BB6_TEXT), max_steps=60_000)
        self.assertEqual(
            events,
            [
                {"step": 140, "params": [0, 0, 2, 0, 0]},
                {"step": 27965, "params": [3, 7, 2, 6, 63]},
            ],
        )

    def test_bb6_s1_rules_on_constructed_tapes(self) -> None:
        table = parse(BB6_TEXT)
        for params in [(3, 5, 2, 3, 3), (2, 2, 0, 1, 1), (2, 0, 1, 3, 2), (2, 0, 0, 3, 2)]:
            with self.subTest(params=params):
                result = check_bb6_s1_case(table, params)
                self.assertTrue(result["ok"], result)


class PatternAndSatTests(unittest.TestCase):
    def test_bb7_low_rule_l1_is_symbolically_proved(self) -> None:
        n = Expr.var("n")
        result = verify_pattern_rule(
            parse(BB7_TEXT),
            PatternRule(
                "bb7_low_rule_L1",
                initial=(cells("011"), rep("01", n), cells("0011100")),
                expected=(cells("1"), rep("01", n + 2), cells("0011100")),
                assumptions={"n": ("ge", 0)},
            ),
        )
        self.assertEqual(result.status, "proved", result.branches)

    def test_sat_engine_finds_a_concrete_transfer_machine(self) -> None:
        instances = reachable_instances(
            [CounterConfig(0, (digit,)) for digit in range(3)],
            encoding=BlockEncoding(0, "n_right"),
            max_steps=40,
        )
        result = synthesize_sat(
            instances, n_states=3, max_steps_cap=40, workspace_slack=3
        )
        if result.status == "error":
            self.skipTest(f"SAT backend unavailable: {result.stats}")
        self.assertTrue(result.found, result.stats)
        for instance in instances:
            self.assertEqual(instance.evaluate(result.table).status, "pass")


class TokenEncodingTests(unittest.TestCase):
    def test_round_trips_and_champion_passes_its_own_instances(self) -> None:
        encoding = TokenEncoding()
        for config in [
            CounterConfig(0, (0,)),
            CounterConfig(2, (1, 0, 3)),
            CounterConfig(5, (0, 2)),
        ]:
            with self.subTest(config=config):
                encoded = encoding.encode(config)
                self.assertEqual(
                    encoding.decode_relative(
                        encoded.relative_ones(), len(config.digits)
                    ),
                    config,
                )
        params = TemplateParams(
            refill="2n+c",
            refill_const=2,
            successor="double",
            successor_const=2,
            consume_refill=True,
        )
        instances = reachable_instances(
            [initial_config(0, 2), initial_config(1, 2), CounterConfig(0, (0, 0))],
            params=params,
            encoding=encoding,
            max_total=10,
            workspace_slack=64,
            checkpoint_test=b_form_checkpoint_test,
        )
        champion = parse(BB7_TEXT)
        self.assertTrue(instances)
        for instance in instances:
            with self.subTest(instance=instance.name):
                self.assertEqual(instance.evaluate(champion).status, "pass")

    def test_pair_transfer_lemma_is_symbolically_proved(self) -> None:
        u, v, d, f = (Expr.var(name) for name in ("u", "v", "d", "f"))

        def tape(suffix_pairs):
            parts = [cells("11")]
            for exponent in [f.scale(3) + 1, d.scale(3) + 4]:
                parts += [cells("1"), rep("01", exponent)]
            for exponent in suffix_pairs:
                parts += [cells("1"), rep("01", exponent)]
            parts += [cells("0011100")]
            return tuple(parts)

        result = verify_pattern_rule(
            parse(BB7_TEXT),
            PatternRule(
                "bb7_pair_transfer_lemma",
                initial=tape([u, v]),
                expected=tape([u - 1, v + 2]),
                assumptions={
                    "u": ("ge", 1),
                    "v": ("ge", 1),
                    "d": ("ge", 0),
                    "f": ("ge", 0),
                },
            ),
        )
        self.assertEqual(result.status, "proved", result.branches)


class CertificationAndGrowthTests(unittest.TestCase):
    def test_certified_whole_run_for_offset_zero_candidate(self) -> None:
        encoding = BlockEncoding(0, "n_right")
        table = parse("0RB1RB_1RC1LB_0RZ0LA")
        proof = verify_counter_step_symbolic(table, n_digits=1, encoding=encoding)
        self.assertTrue(proof.proved)
        certified = certified_run(
            table,
            start=CounterConfig(0, (60,)),
            symbolic_result=proof,
            encoding=encoding,
        )
        self.assertTrue(certified.halted)
        self.assertEqual(certified.final, CounterConfig(60, (0,)))
        self.assertEqual(certified.abstract_steps, 60)
        # Symbolic branches: successor costs 4 steps at n = 0 and n = 1,
        # then 3 steps for n >= 2; the final halt leg costs 2 steps.
        self.assertEqual(certified.tm_steps, 4 + 4 + 58 * 3 + 2)
        self.assertEqual(
            abstract_lower_bound(CounterConfig(0, (60,))), 61
        )
        self.assertLessEqual(certified.lower_bound_steps, certified.tm_steps)

    def test_digit_clearing_closed_form(self) -> None:
        self.assertEqual([clear_digit_final_a(0, v) for v in range(6)], [0, 2, 6, 14, 30, 62])
        params = TemplateParams(
            successor="double", successor_const=2, consume_refill=True
        )
        run = run_counter(CounterConfig(0, (5, 0)), params)
        self.assertTrue(run.halted)
        self.assertEqual(run.final.n, clear_digit_final_a(0, 5))

    def test_consuming_doubling_dominates_textbook_on_sample_grid(self) -> None:
        report = domination_samples(max_n=2, max_digit=2, n_digits=2)
        self.assertEqual(report["failures"], [])
        self.assertEqual(report["final_dominated"], report["checked"])
        self.assertEqual(report["steps_dominated"], report["checked"])


if __name__ == "__main__":
    unittest.main()
