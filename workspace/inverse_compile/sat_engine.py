"""Engine B: SAT bounded-model-checking synthesis.

Given concrete checkpoint instances and a state budget, encode the unknown
transition table and one bounded trace per instance as SAT.  A trace is
accepted at the first time its tape equals the expected checkpoint pattern
(or at halt, for halting instances); steps after acceptance are left
unconstrained.  The extracted table is always rechecked with the concrete
simulator by callers before it is trusted.

This complements Engine A's depth-first search: the SAT solver's conflict
learning handles the non-local interactions (copy/doubling loops) on which
depth-first branching thrashes, at the cost of a much larger encoding.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from .instances import Instance
from .tm import HALT, Table, empty_table


@dataclass
class SatResult:
    status: str  # sat, unsat, error
    table: Table | None
    stats: dict = field(default_factory=dict)

    @property
    def found(self) -> bool:
        return self.status == "sat" and self.table is not None


def _solver_names():
    return ("cd19", "cd15", "cadical195", "g3", "g4", "mcb", "minisat22")


def synthesize_sat(
    instances: list[Instance],
    *,
    n_states: int,
    initial_table: Table | None = None,
    max_steps_cap: int = 250,
    workspace_slack: int = 8,
    solver_name: str | None = None,
) -> SatResult:
    """Search for a total table satisfying every instance within its bound."""
    try:
        from pysat.card import CardEnc, EncType
        from pysat.formula import IDPool
        from pysat.solvers import Solver
    except Exception as exc:  # pragma: no cover - environment dependent
        return SatResult("error", None, {"error": f"PySAT unavailable: {exc}"})

    started = time.monotonic()
    pool = IDPool()
    clauses: list[list[int]] = []

    def var(*key) -> int:
        return pool.id(key)

    def exactly_one(lits: list[int]) -> None:
        clauses.extend(
            CardEnc.equals(lits=lits, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses
        )

    halt_index = n_states  # next-state / state index representing HALT
    # Transition-table variables.
    for q in range(n_states):
        for s in (0, 1):
            exactly_one([var("next", q, s, k) for k in range(n_states + 1)])
    if initial_table is not None:
        for q, row in enumerate(initial_table):
            for s, entry in enumerate(row):
                if entry is None:
                    continue
                w, d, ns = entry
                clauses.append([var("write", q, s) if w else -var("write", q, s)])
                clauses.append([var("dir", q, s) if d > 0 else -var("dir", q, s)])
                clauses.append([var("next", q, s, halt_index if ns == HALT else ns)])

    for ii, inst in enumerate(instances):
        start = inst.start
        expected = inst.expected_ones or frozenset()
        points = set(start.ones) | {start.head}
        if expected:
            points |= {start.head + min(expected), start.head + max(expected)}
        lo = min(points) - workspace_slack
        hi = max(points) + workspace_slack
        positions = list(range(lo, hi + 1))
        steps = max(1, min(inst.max_steps, max_steps_cap))
        checkpoint = inst.checkpoint_state

        def cell(t, p):
            return var("cell", ii, t, p)

        def headv(t, p):
            return var("head", ii, t, p)

        def statev(t, q):
            return var("state", ii, t, q)

        def done(t):
            return var("done", ii, t)

        # Initial configuration and one-hot constraints.
        for p in positions:
            clauses.append([cell(0, p) if p in start.ones else -cell(0, p)])
        clauses.append([headv(0, start.head)])
        clauses.append([statev(0, start.state)])
        for t in range(steps + 1):
            exactly_one([headv(t, p) for p in positions])
            exactly_one([statev(t, q) for q in range(n_states + 1)])
        clauses.append([-done(0)])
        clauses.append([done(steps)])
        for t in range(1, steps + 1):
            clauses.append([-done(t - 1), done(t)])  # monotone
            # Reaching the checkpoint state (or HALT) implies acceptance.
            clauses.append([-statev(t, checkpoint), done(t)])
            clauses.append([-statev(t, halt_index), done(t)])
            if inst.expect_halt:
                # Acceptance moment must be the halt state.
                clauses.append([-done(t), done(t - 1), statev(t, halt_index)])
            else:
                clauses.append([-done(t), done(t - 1), statev(t, checkpoint)])
                # Halting before acceptance is forbidden (done(t) would be
                # forced, but the acceptance moment requires checkpoint).
                for p in positions:
                    fits = all(lo <= p + off <= hi for off in expected)
                    if not fits:
                        clauses.append([-done(t), done(t - 1), -headv(t, p)])
                        continue
                    for x in positions:
                        bit = 1 if (x - p) in expected else 0
                        clauses.append(
                            [
                                -done(t),
                                done(t - 1),
                                -headv(t, p),
                                cell(t, x) if bit else -cell(t, x),
                            ]
                        )

        # Trace transitions, guarded by "not yet accepted".
        for t in range(steps):
            guard = done(t)
            hc = var("hc", ii, t)  # symbol under the head
            for p in positions:
                clauses.append([guard, -headv(t, p), -cell(t, p), hc])
                clauses.append([guard, -headv(t, p), cell(t, p), -hc])
            for q in range(n_states):
                for s in (0, 1):
                    tr = var("tr", ii, t, q, s)
                    hclit = hc if s else -hc
                    clauses.append([-tr, statev(t, q)])
                    clauses.append([-tr, hclit])
                    clauses.append([-statev(t, q), -hclit, tr])
                    wvar = var("write", q, s)
                    dvar = var("dir", q, s)
                    for k in range(n_states + 1):
                        clauses.append(
                            [guard, -tr, -var("next", q, s, k), statev(t + 1, k)]
                        )
                    for pi, p in enumerate(positions):
                        clauses.append(
                            [guard, -headv(t, p), -tr, -wvar, cell(t + 1, p)]
                        )
                        clauses.append(
                            [guard, -headv(t, p), -tr, wvar, -cell(t + 1, p)]
                        )
                        if pi + 1 < len(positions):
                            clauses.append(
                                [guard, -headv(t, p), -tr, -dvar, headv(t + 1, p + 1)]
                            )
                        else:
                            clauses.append([guard, -headv(t, p), -tr, -dvar])
                        if pi > 0:
                            clauses.append(
                                [guard, -headv(t, p), -tr, dvar, headv(t + 1, p - 1)]
                            )
                        else:
                            clauses.append([guard, -headv(t, p), -tr, dvar])
            # Frame: cells away from the head are unchanged.
            for p in positions:
                for x in positions:
                    if x == p:
                        continue
                    clauses.append([guard, -headv(t, p), -cell(t, x), cell(t + 1, x)])
                    clauses.append([guard, -headv(t, p), cell(t, x), -cell(t + 1, x)])

    stats = {"variables": pool.top, "clauses": len(clauses)}
    names = (solver_name,) if solver_name else _solver_names()
    last_error = None
    for name in names:
        try:
            with Solver(name=name, bootstrap_with=clauses) as solver:
                sat = solver.solve()
                stats["solver"] = name
                stats["elapsed_s"] = time.monotonic() - started
                if not sat:
                    return SatResult("unsat", None, stats)
                model = set(solver.get_model() or [])
                table = empty_table(n_states)
                for q in range(n_states):
                    for s in (0, 1):
                        w = 1 if var("write", q, s) in model else 0
                        d = 1 if var("dir", q, s) in model else -1
                        ns = next(
                            k
                            for k in range(n_states + 1)
                            if var("next", q, s, k) in model
                        )
                        table[q][s] = (w, d, HALT if ns == halt_index else ns)
                return SatResult("sat", table, stats)
        except Exception as exc:  # try the next bundled solver
            last_error = exc
            continue
    stats["error"] = str(last_error)
    stats["elapsed_s"] = time.monotonic() - started
    return SatResult("error", None, stats)
