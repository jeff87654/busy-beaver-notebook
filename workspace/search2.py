"""Round 2: evolve from round-1 winners with deeper verification budgets.

Run: python search2.py <seconds> <infile-merged.json> <outfile-prefix>
"""
import json
import multiprocessing as mp
import random
import sys
import time

from sim import parse, fmt, simulate, HALT
from search import random_table, seeded_table, mutate, N

EVAL_OPS = 5_000
DEEP_OPS = 1_000_000


def evaluate(table):
    st, steps, ones, ops = simulate(table, max_ops=EVAL_OPS)
    if st == "ops" and steps > 50_000:
        st, steps, ones, ops = simulate(table, max_ops=DEEP_OPS)
    return st, steps, ones


def worker(args):
    wid, seconds, prefix, elites = args
    rng = random.Random(0xFACE + wid * 104729)
    deadline = time.time() + seconds
    best = []
    unresolved = []
    sims = 0
    halters = 0

    while time.time() < deadline:
        r = rng.random()
        if elites and r < 0.6:
            table = parse(rng.choice(elites))
            # elite tables may carry several halts after parsing; fine —
            # mutate() only relocates the first one it finds
        elif r < 0.75:
            table = seeded_table(rng)
        else:
            table = random_table(rng)
        st, steps, ones = evaluate(table)
        sims += 1
        score = steps if st == "halt" else 0
        if st == "halt":
            halters += 1
        if st == "ops" and steps > 10**10:
            unresolved.append((steps, fmt(table)))
        stale = 0
        while stale < 600 and time.time() < deadline:
            cand = mutate(table, rng)
            cst, csteps, cones = evaluate(cand)
            sims += 1
            if cst == "halt":
                halters += 1
                if csteps > score:
                    table, score, ones = cand, csteps, cones
                    stale = 0
                    continue
            elif cst == "ops" and csteps > 10**10:
                unresolved.append((csteps, fmt(cand)))
            stale += 1
        if score > 0:
            best.append((score, ones, fmt(table)))
            best.sort(reverse=True)
            del best[20:]
        unresolved.sort(reverse=True)
        del unresolved[10:]

    out = {"worker": wid, "sims": sims, "halters": halters,
           "best": best, "unresolved": unresolved}
    with open(f"{prefix}_w{wid}.json", "w") as f:
        json.dump(out, f)
    return out


def main():
    seconds = int(sys.argv[1])
    infile = sys.argv[2]
    prefix = sys.argv[3]
    with open(infile) as f:
        merged = json.load(f)
    elites = [t for _, _, t in merged["best"][:30]]
    nproc = max(1, (mp.cpu_count() or 4) - 2)
    with mp.Pool(nproc) as pool:
        results = pool.map(
            worker, [(w, seconds, prefix, elites) for w in range(nproc)])

    allbest = sorted((tuple(b) for r in results for b in r["best"]),
                     reverse=True)
    allunres = sorted((tuple(u) for r in results for u in r["unresolved"]),
                      reverse=True)
    total = sum(r["sims"] for r in results)
    halt = sum(r["halters"] for r in results)
    print(f"simulated {total} machines ({halt} halters) on {nproc} workers")
    print("\n=== top verified halters (steps, ones, machine) ===")
    for s, o, t in allbest[:10]:
        print(f"{s:>20}  {o:>12}  {t}")
    print("\n=== top unresolved (steps at cutoff) ===")
    for s, t in allunres[:10]:
        print(f"{float(s):.3e}  {t}")
    with open(f"{prefix}_merged.json", "w") as f:
        json.dump({"best": allbest[:50], "unresolved": allunres[:20],
                   "sims": total, "halters": halt}, f)


if __name__ == "__main__":
    main()
