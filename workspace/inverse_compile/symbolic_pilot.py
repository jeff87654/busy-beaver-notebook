"""Record symbolic one-step proofs for the calibration machines.

Run from the workspace root::

    python -m inverse_compile.symbolic_pilot

A ``proved`` record means that every symbolic case branch reached the
expected first checkpoint (or halt in the all-zero case) with the exact
expected tape pattern.  It proves one abstract simulation step, not a
blank-tape Busy Beaver lower bound by itself.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .encoding import BlockEncoding
from .sketches import successor_sketch
from .symbolic import SymbolicResult, verify_counter_step_symbolic
from .tm import format_table, parse


def _record(name: str, table_text: str, n_digits: int, result: SymbolicResult):
    return {
        "name": name,
        "table": table_text,
        "n_digits": n_digits,
        "status": result.status,
        "explored": result.explored,
        "branches": [asdict(branch) for branch in result.branches],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("inverse_compile/results/symbolic_pilot.json"),
    )
    args = parser.parse_args()

    runs = []
    specs = [
        (
            "discovered_transfer1_offset0_nright",
            "0RB1RB_1RC1LB_0RZ0LA",
            BlockEncoding(0, "n_right"),
            1,
        ),
        (
            "discovered_transfer1_offset1_nright",
            "---1RB_0RB1RC_1RD1LC_0RZ0LA",
            BlockEncoding(1, "n_right"),
            1,
        ),
        (
            "hand_built_transfer1_offset0_left_sweep",
            "1RC1RB_1RC1RB_0RZ0LD_0RA1LD",
            BlockEncoding(0, "left"),
            1,
        ),
        (
            "negative_control_always_halt",
            "1RZ1RZ",
            BlockEncoding(1, "n_right"),
            1,
        ),
    ]
    for name, text, encoding, n_digits in specs:
        result = verify_counter_step_symbolic(
            parse(text), n_digits=n_digits, encoding=encoding
        )
        record = _record(name, text, n_digits, result)
        record["encoding"] = asdict(encoding)
        runs.append(record)
        print(f"{name}: {result.status} ({len(result.branches)} branches)")

    sketch = successor_sketch(6)
    sketch_encoding = BlockEncoding(1, "n_right")
    sketch_result = verify_counter_step_symbolic(
        sketch, n_digits=2, encoding=sketch_encoding
    )
    sketch_record = _record(
        "successor_sketch_counter2_offset1_nright",
        format_table(sketch),
        2,
        sketch_result,
    )
    sketch_record["encoding"] = asdict(sketch_encoding)
    runs.append(sketch_record)
    print(
        "successor_sketch_counter2_offset1_nright: "
        f"{sketch_result.status} ({len(sketch_result.branches)} branches)"
    )

    payload = {
        "warning": (
            "These records prove one abstract checkpoint-to-checkpoint step "
            "for the stated fixed digit length and encoding. They do not "
            "supply blank-tape initialization, iteration, ordinal descent, "
            "or a Busy Beaver bound."
        ),
        "records": runs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
