"""Reproducible Engine-A calibration pilot.

Run from the workspace root, for example::

    python -m inverse_compile.pilot --profile full

The pilot measures the two behaviors that determine whether the larger
project is viable: whether specification pruning finds separator-shifting
counters, and how sharply the search grows at the first refill/copy step.
A result labelled ``pass_bounded`` is a finite-box check, never a proof for
all block lengths.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .abstract import CounterConfig, TemplateParams, initial_config
from .encoding import BlockEncoding
from .engine import SearchResult, synthesize_with_holdout
from .instances import reachable_instances
from .sketches import successor_sketch
from .tm import Table, complete_table, format_table
from .verify import VerificationResult, verify_box


def _verification_record(result: VerificationResult | None) -> dict[str, Any] | None:
    if result is None:
        return None
    record: dict[str, Any] = {"status": result.status, "checked": result.checked}
    if result.evaluation is not None:
        record["instance"] = result.evaluation.instance.name
        record["outcome"] = result.evaluation.outcome.status
        record["reason"] = result.evaluation.reason
    return record


def _record(
    *,
    experiment: str,
    n_states: int,
    train_count: int,
    holdout_count: int,
    result: SearchResult,
    verification: VerificationResult | None = None,
) -> dict[str, Any]:
    partial = format_table(result.table) if result.table is not None else None
    completed = (
        format_table(complete_table(result.table)) if result.table is not None else None
    )
    return {
        "experiment": experiment,
        "n_states": n_states,
        "train_instances": train_count,
        "holdout_instances": holdout_count,
        "status": result.status,
        "partial_table": partial,
        "completed_table_arbitrary_fill": completed,
        "rounds": result.rounds,
        "added_instances": result.added_instances,
        "stats": asdict(result.stats),
        "bounded_verification_of_partial_table": _verification_record(verification),
    }


def _print_record(record: dict[str, Any]) -> None:
    stats = record["stats"]
    print(
        f"{record['experiment']} N={record['n_states']}: {record['status']} "
        f"nodes={stats['nodes']} evaluations={stats['evaluations']} "
        f"elapsed={stats['elapsed_s']:.2f}s table={record['partial_table']}",
        flush=True,
    )
    verification = record["bounded_verification_of_partial_table"]
    if verification is not None:
        print(
            f"  bounded verification: {verification['status']} "
            f"checked={verification['checked']}",
            flush=True,
        )


def _transfer_sets(offset: int):
    encoding = BlockEncoding(offset, head_anchor="n_right")
    train = reachable_instances(
        [CounterConfig(0, (digit,)) for digit in range(4)],
        encoding=encoding,
        max_steps=100,
    )
    holdout = reachable_instances(
        [CounterConfig(0, (digit,)) for digit in (4, 5)],
        encoding=encoding,
        max_steps=100,
    )
    return encoding, train, holdout


def run_transfer(*, node_budget: int, time_budget_s: float) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    state_counts = {0: (2, 3), 1: (3, 4)}
    for offset, counts in state_counts.items():
        encoding, train, holdout = _transfer_sets(offset)
        for n_states in counts:
            result = synthesize_with_holdout(
                train,
                holdout,
                n_states=n_states,
                node_budget_per_round=node_budget,
                time_budget_per_round_s=time_budget_s,
            )
            verification = None
            if result.table is not None:
                verification = verify_box(
                    result.table,
                    max_n=5,
                    max_digit=5,
                    n_digits=1,
                    encoding=encoding,
                )
            record = _record(
                experiment=f"transfer1_offset{offset}_nright",
                n_states=n_states,
                train_count=len(train),
                holdout_count=len(holdout),
                result=result,
                verification=verification,
            )
            records.append(record)
            _print_record(record)
            if result.found:
                break
    return records


def _counter2_sets():
    encoding = BlockEncoding(1, head_anchor="n_right")
    train = reachable_instances(
        [initial_config(1, 2), initial_config(2, 2), CounterConfig(0, (0, 0))],
        encoding=encoding,
    )
    holdout = reachable_instances(
        [initial_config(3, 2), CounterConfig(2, (0, 2))],
        encoding=encoding,
    )
    return encoding, train, holdout


def _verify_counter2(
    table: Table,
    encoding: BlockEncoding,
    params: TemplateParams = TemplateParams(),
) -> VerificationResult:
    return verify_box(
        table, max_n=4, max_digit=3, n_digits=2, params=params, encoding=encoding
    )


def run_counter2(
    *, node_budget: int, time_budget_s: float, sketch_node_budget: int
) -> list[dict[str, Any]]:
    encoding, train, holdout = _counter2_sets()
    records: list[dict[str, Any]] = []

    for n_states in (4, 5, 6):
        result = synthesize_with_holdout(
            train,
            holdout,
            n_states=n_states,
            node_budget_per_round=node_budget,
            time_budget_per_round_s=time_budget_s,
        )
        verification = _verify_counter2(result.table, encoding) if result.table else None
        record = _record(
            experiment="counter2_offset1_nright_free",
            n_states=n_states,
            train_count=len(train),
            holdout_count=len(holdout),
            result=result,
            verification=verification,
        )
        records.append(record)
        _print_record(record)
        if result.found:
            return records

    for n_states in (6, 7):
        result = synthesize_with_holdout(
            train,
            holdout,
            n_states=n_states,
            initial_table=successor_sketch(n_states),
            node_budget_per_round=sketch_node_budget,
            time_budget_per_round_s=max(time_budget_s, 60.0),
        )
        verification = _verify_counter2(result.table, encoding) if result.table else None
        record = _record(
            experiment="counter2_offset1_nright_successor_sketch",
            n_states=n_states,
            train_count=len(train),
            holdout_count=len(holdout),
            result=result,
            verification=verification,
        )
        records.append(record)
        _print_record(record)
        if result.found:
            break
    return records


def run_counter2_consuming(
    *, node_budget: int, time_budget_s: float
) -> list[dict[str, Any]]:
    """Champion-inspired variant: doubling successor, consuming refill.

    The BB(7) champion never copies its accumulator: successor steps grow
    it (there, by doubling) and refill moves it into a digit and resets it
    to zero.  This experiment asks whether that architecture is easier for
    Engine A than exact-copy refill in unary blocks.
    """
    params = TemplateParams(
        refill="2n+c",
        refill_const=2,
        successor="double",
        successor_const=2,
        consume_refill=True,
    )
    encoding = BlockEncoding(1, head_anchor="n_right")
    train = reachable_instances(
        [initial_config(0, 2), initial_config(1, 2), initial_config(2, 2), CounterConfig(0, (0, 0))],
        params=params,
        encoding=encoding,
        max_total=40,
    )
    holdout = reachable_instances(
        [initial_config(3, 2), CounterConfig(1, (0, 2))],
        params=params,
        encoding=encoding,
        max_total=60,
    )
    records: list[dict[str, Any]] = []
    for n_states in (5, 6, 7):
        result = synthesize_with_holdout(
            train,
            holdout,
            n_states=n_states,
            node_budget_per_round=node_budget,
            time_budget_per_round_s=time_budget_s,
        )
        verification = (
            _verify_counter2(result.table, encoding, params) if result.table else None
        )
        record = _record(
            experiment="counter2_consuming_doubling_offset1_nright_free",
            n_states=n_states,
            train_count=len(train),
            holdout_count=len(holdout),
            result=result,
            verification=verification,
        )
        records.append(record)
        _print_record(record)
        if result.found:
            break
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile", choices=("quick", "full"), default="full",
        help="quick uses smaller node budgets for a smoke run",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="JSON output path (default depends on profile)",
    )
    parser.add_argument(
        "--skip-counter2", action="store_true", help="run only one-digit transfers"
    )
    args = parser.parse_args()

    if args.profile == "quick":
        transfer_budget, counter_budget, sketch_budget = 30_000, 20_000, 20_000
        time_budget = 15.0
        output = args.output or Path("inverse_compile/results/pilot_quick.json")
    else:
        transfer_budget, counter_budget, sketch_budget = 30_000, 60_000, 120_000
        time_budget = 30.0
        output = args.output or Path("inverse_compile/results/pilot_full.json")

    records = run_transfer(node_budget=transfer_budget, time_budget_s=time_budget)
    if not args.skip_counter2:
        records.extend(
            run_counter2(
                node_budget=counter_budget,
                time_budget_s=time_budget,
                sketch_node_budget=sketch_budget,
            )
        )
        records.extend(
            run_counter2_consuming(
                node_budget=counter_budget, time_budget_s=time_budget
            )
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "profile": args.profile,
        "warning": (
            "Candidates are rule fragments checked on finite instance sets. "
            "pass_bounded is not a proof for arbitrary block lengths, and no "
            "blank-tape initialization or BB lower bound is claimed."
        ),
        "records": records,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
