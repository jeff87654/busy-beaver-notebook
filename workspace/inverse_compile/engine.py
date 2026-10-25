"""Engine A: depth-first, specification-pruned transition synthesis.

The partial transition table is run on every concrete test instance.  A
deterministic failure prunes the branch.  If all completed instances pass and
some instance reaches an unassigned transition, the search branches over the
possible assignments for that transition.  New states are introduced only in
numeric order, which removes state-renaming duplicates from the pilot search.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from .instances import Evaluation, Instance
from .tm import HALT, Table, Transition, copy_table, empty_table


@dataclass
class SearchStats:
    nodes: int = 0
    evaluations: int = 0
    branches: int = 0
    max_depth: int = 0
    elapsed_s: float = 0.0
    prunes: dict[str, int] = field(default_factory=dict)

    def record_prune(self, evaluation: Evaluation) -> None:
        if evaluation.reason.startswith("wrong"):
            key = evaluation.reason
        elif evaluation.reason.startswith("expected"):
            key = evaluation.reason
        else:
            key = evaluation.outcome.status
        self.prunes[key] = self.prunes.get(key, 0) + 1

    def absorb(self, other: "SearchStats") -> None:
        self.nodes += other.nodes
        self.evaluations += other.evaluations
        self.branches += other.branches
        self.max_depth = max(self.max_depth, other.max_depth)
        self.elapsed_s += other.elapsed_s
        for key, value in other.prunes.items():
            self.prunes[key] = self.prunes.get(key, 0) + value


@dataclass
class SearchResult:
    status: str  # candidate, exhausted, node_budget, time_budget
    table: Table | None
    stats: SearchStats
    rounds: int = 1
    added_instances: list[str] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return self.status == "candidate" and self.table is not None


class _BudgetExceeded(Exception):
    def __init__(self, status: str):
        super().__init__(status)
        self.status = status


def _used_states(table: Table, instances: list[Instance]) -> set[int]:
    used = {0}
    for instance in instances:
        used.add(instance.start.state)
        used.add(instance.checkpoint_state)
    for state, row in enumerate(table):
        for entry in row:
            if entry is not None:
                used.add(state)
                if entry[2] != HALT:
                    used.add(entry[2])
    return {state for state in used if 0 <= state < len(table)}


def _options(
    table: Table,
    instances: list[Instance],
    branch: tuple[int, int],
    branch_instance: Instance,
) -> list[Transition]:
    state, symbol = branch
    used = _used_states(table, instances)
    next_states: list[int] = []

    def add(candidate: int) -> None:
        if candidate not in next_states:
            next_states.append(candidate)

    add(state)
    add(branch_instance.checkpoint_state)
    add(0)
    for candidate in sorted(used):
        add(candidate)
    for candidate in range(len(table)):
        if candidate not in used:
            add(candidate)
            break
    add(HALT)

    scored: list[tuple[int, Transition]] = []
    for next_index, next_state in enumerate(next_states):
        for write in (symbol, 1 - symbol):
            for direction in (1, -1):
                score = next_index
                if write != symbol:
                    score += 2
                if direction < 0:
                    score += 1
                if next_state == HALT:
                    score += 2 if branch_instance.expect_halt else 8
                scored.append((score, (write, direction, next_state)))
    scored.sort(key=lambda item: item[0])
    return [entry for _, entry in scored]


def synthesize(
    instances: list[Instance],
    *,
    n_states: int,
    initial_table: Table | None = None,
    node_budget: int = 100_000,
    time_budget_s: float = 30.0,
) -> SearchResult:
    """Search for a partial table that passes every supplied instance."""
    if n_states < 1:
        raise ValueError("n_states must be positive")
    table = copy_table(initial_table) if initial_table is not None else empty_table(n_states)
    if len(table) != n_states or any(len(row) != 2 for row in table):
        raise ValueError("initial_table does not match n_states")
    stats = SearchStats()
    started = time.monotonic()

    def check_budget() -> None:
        if stats.nodes > node_budget:
            raise _BudgetExceeded("node_budget")
        if time.monotonic() - started > time_budget_s:
            raise _BudgetExceeded("time_budget")

    def evaluate_all() -> tuple[str, Evaluation | None]:
        first_undef: Evaluation | None = None
        for instance in instances:
            evaluation = instance.evaluate(table)
            stats.evaluations += 1
            if evaluation.status == "fail":
                # Adding an unrelated unassigned transition cannot change a
                # deterministic run that never encountered one.
                return ("fail", evaluation)
            if evaluation.status == "undef" and first_undef is None:
                first_undef = evaluation
        if first_undef is not None:
            return ("undef", first_undef)
        return ("pass", None)

    def assigned_depth() -> int:
        return sum(entry is not None for row in table for entry in row)

    def dfs() -> Table | None:
        stats.nodes += 1
        stats.max_depth = max(stats.max_depth, assigned_depth())
        check_budget()
        kind, evaluation = evaluate_all()
        if kind == "pass":
            return copy_table(table)
        if kind == "fail":
            assert evaluation is not None
            stats.record_prune(evaluation)
            return None
        assert evaluation is not None and evaluation.outcome.undef is not None
        branch = evaluation.outcome.undef
        state, symbol = branch
        for entry in _options(table, instances, branch, evaluation.instance):
            stats.branches += 1
            table[state][symbol] = entry
            try:
                found = dfs()
            finally:
                table[state][symbol] = None
            if found is not None:
                return found
            check_budget()
        return None

    try:
        candidate = dfs()
        status = "candidate" if candidate is not None else "exhausted"
    except _BudgetExceeded as exc:
        candidate = None
        status = exc.status
    stats.elapsed_s = time.monotonic() - started
    return SearchResult(status=status, table=candidate, stats=stats)


def synthesize_with_holdout(
    train: list[Instance],
    holdout: list[Instance],
    *,
    n_states: int,
    initial_table: Table | None = None,
    node_budget_per_round: int = 100_000,
    time_budget_per_round_s: float = 30.0,
    max_rounds: int = 20,
) -> SearchResult:
    """A small CEGIS loop over a fixed train/holdout split.

    A concrete holdout failure is promoted into the training set and synthesis
    restarts.  A holdout run that merely reaches an unused transition is also
    promoted, but synthesis resumes from the current partial candidate.
    """
    current = list(train)
    known_names = {instance.name for instance in current}
    sketch = copy_table(initial_table) if initial_table is not None else None
    active_initial_table = sketch
    total_stats = SearchStats()
    added: list[str] = []

    for round_index in range(1, max_rounds + 1):
        result = synthesize(
            current,
            n_states=n_states,
            initial_table=active_initial_table,
            node_budget=node_budget_per_round,
            time_budget_s=time_budget_per_round_s,
        )
        total_stats.absorb(result.stats)
        if not result.found:
            return SearchResult(
                status=result.status,
                table=None,
                stats=total_stats,
                rounds=round_index,
                added_instances=added,
            )
        assert result.table is not None
        evaluations = [instance.evaluate(result.table) for instance in holdout]
        failure = next((ev for ev in evaluations if ev.status == "fail"), None)
        undef = next((ev for ev in evaluations if ev.status == "undef"), None)
        if failure is None and undef is None:
            return SearchResult(
                status="candidate",
                table=result.table,
                stats=total_stats,
                rounds=round_index,
                added_instances=added,
            )
        chosen = failure if failure is not None else undef
        assert chosen is not None
        if chosen.instance.name not in known_names:
            current.append(chosen.instance)
            known_names.add(chosen.instance.name)
            added.append(chosen.instance.name)
        active_initial_table = result.table if failure is None else sketch

    return SearchResult(
        status="round_budget",
        table=None,
        stats=total_stats,
        rounds=max_rounds,
        added_instances=added,
    )
