"""Heuristic search for long-running halting 8-state 2-symbol Turing machines.

Strategy: hill climbing with random restarts. A machine's score is its exact
step count if it provably halts within the op budget, else 0. Some restarts
seed from known busy beaver champions embedded in an 8-state table so the
spare states can evolve into amplifiers. Machines that exhaust the op budget
at a large step count are logged separately as unresolved candidates.

Run: python search.py <seconds> <outfile-prefix>
Spawns one worker per core via multiprocessing.
"""
import json
import multiprocessing as mp
import random
import sys
import time

from sim import parse, fmt, simulate, HALT

N = 8
EVAL_OPS = 3_000
SEEDS = [
    "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA",            # BB(5) champion
    "1RB1LB_1LA0LC_1RZ1LD_1RD0RA",                   # BB(4) champion
    "1RB0LD_1RC0RF_1LC1LA_0LE1RZ_1LF0RB_0RC0RE",     # BB(6) champ (10^^15)
    "1RB1LE_1RC1RF_1LD0RB_1RE0LC_1LA0RD_1RZ1RC",     # BB(6) 10^36534 machine
]


def random_entry(rng):
    return (rng.randint(0, 1), rng.choice((1, -1)), rng.randrange(N))


def random_table(rng):
    table = [[random_entry(rng), random_entry(rng)] for _ in range(N)]
    table[0][0] = (1, 1, 1)  # normal form: A0 = 1RB
    # exactly one halt transition, writing 1 (championship convention)
    s = rng.randrange(1, N)
    table[s][rng.randint(0, 1)] = (1, 1, HALT)
    return table


def seeded_table(rng):
    base = parse(rng.choice(SEEDS))
    k = len(base)
    table = [[e if e else random_entry(rng) for e in row] for row in base]
    while len(table) < N:
        table.append([random_entry(rng), random_entry(rng)])
    # redirect the seed's halt into the spare states, put a halt out there
    halts = [(i, j) for i in range(k) for j in (0, 1)
             if table[i][j][2] == HALT]
    for (i, j) in halts:
        w, d, _ = table[i][j]
        table[i][j] = (w, d, rng.randrange(k, N))
    s = rng.randrange(k, N)
    table[s][rng.randint(0, 1)] = (1, 1, HALT)
    return table


def halt_positions(table):
    return [(i, j) for i in range(N) for j in (0, 1)
            if table[i][j] is not None and table[i][j][2] == HALT]


def mutate(table, rng):
    t = [row[:] for row in table]
    kind = rng.random()
    i = rng.randrange(N)
    j = rng.randint(0, 1)
    while i == 0 and j == 0:  # keep normal form A0=1RB
        i = rng.randrange(N)
        j = rng.randint(0, 1)
    if kind < 0.15:
        # move the halt transition somewhere else
        hp = halt_positions(t)
        if hp:
            hi, hj = hp[0]
            w, d, _ = t[hi][hj]
            t[hi][hj] = (w, d, rng.randrange(N))
        t[i][j] = (1, rng.choice((1, -1)), HALT)
    else:
        if t[i][j][2] == HALT:
            return t  # don't destroy the only halt; try again next round
        w, d, ns = t[i][j]
        r = rng.random()
        if r < 0.33:
            t[i][j] = (1 - w, d, ns)
        elif r < 0.66:
            t[i][j] = (w, -d, ns)
        else:
            t[i][j] = (w, d, rng.randrange(N))
    return t


def evaluate(table):
    st, steps, ones, ops = simulate(table, max_ops=EVAL_OPS)
    if st == "ops" and steps > 50_000:
        # still chain-accelerating at cutoff — worth a deep look
        st, steps, ones, ops = simulate(table, max_ops=300_000)
    return st, steps, ones


def worker(args):
    wid, seconds, prefix = args
    rng = random.Random(0xBEEF + wid * 7919)
    deadline = time.time() + seconds
    best = []          # list of (steps, ones, tm) halters, kept small
    unresolved = []    # (steps_at_cutoff, tm) for op-budget blowups
    sims = 0
    halters = 0

    while time.time() < deadline:
        table = seeded_table(rng) if rng.random() < 0.25 else random_table(rng)
        st, steps, ones = evaluate(table)
        sims += 1
        score = steps if st == "halt" else 0
        if st == "halt":
            halters += 1
        if st == "ops" and steps > 10**12:
            unresolved.append((steps, fmt(table)))
        stale = 0
        while stale < 400 and time.time() < deadline:
            cand = mutate(table, rng)
            cst, csteps, cones = evaluate(cand)
            sims += 1
            if cst == "halt":
                halters += 1
                if csteps > score:
                    table, score, st, steps, ones = cand, csteps, cst, csteps, cones
                    stale = 0
                    continue
            elif cst == "ops" and csteps > 10**12:
                unresolved.append((csteps, fmt(cand)))
            stale += 1
        if score > 0:
            best.append((score, ones, fmt(table)))
            best.sort(reverse=True)
            del best[20:]
        unresolved.sort(reverse=True)
        del unresolved[20:]

    out = {
        "worker": wid, "sims": sims, "halters": halters,
        "best": [(s, o, t) for s, o, t in best],
        "unresolved": [(s, t) for s, t in unresolved],
    }
    with open(f"{prefix}_w{wid}.json", "w") as f:
        json.dump(out, f)
    return out


def main():
    seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    prefix = sys.argv[2] if len(sys.argv) > 2 else "results"
    nproc = max(1, (mp.cpu_count() or 4) - 2)
    with mp.Pool(nproc) as pool:
        results = pool.map(worker, [(w, seconds, prefix) for w in range(nproc)])

    allbest = sorted((b for r in results for b in r["best"]), reverse=True)
    allunres = sorted((u for r in results for u in r["unresolved"]), reverse=True)
    total = sum(r["sims"] for r in results)
    halt = sum(r["halters"] for r in results)
    print(f"simulated {total} machines ({halt} halters) on {nproc} workers")
    print("\n=== top verified halters (steps, ones, machine) ===")
    for s, o, t in allbest[:10]:
        print(f"{s:>20}  {o:>12}  {t}")
    print("\n=== top unresolved: exceeded op budget at step count ===")
    for s, t in allunres[:10]:
        print(f"{s:.3e}  {t}")
    with open(f"{prefix}_merged.json", "w") as f:
        json.dump({"best": allbest[:50], "unresolved": allunres[:50],
                   "sims": total, "halters": halt}, f)


if __name__ == "__main__":
    main()
