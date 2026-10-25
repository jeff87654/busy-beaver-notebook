"""Seeded neutral-drift search of three-state BB(5) postludes.

The BB(5) core is fixed, with E0 redirected to F. Its exact final
configuration is computed once, then copied for each candidate. Cutoffs
are unresolved, never halting or nonhalting proofs. Independent macro
verification is required for any reported record.
"""
import argparse
from collections import Counter
import json
import multiprocessing as mp
import random
import time

from sim import parse, fmt, HALT, _push, _pop1, _ones

BASE = "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RF0LA"


def run(table, limit, initial=None, stop_on_entry=None, stop_before=None):
    if initial is None:
        left, right, state, steps = [], [], 0, 0
    else:
        left, right, state, steps = initial
        left, right = [x[:] for x in left], [x[:] for x in right]
    visited = 0
    for ops in range(1, limit + 1):
        cur = right[-1][0] if right else 0
        if (state, cur) == stop_before:
            return "entry", steps, _ones(left, right), ops - 1, visited, (left, right, state, steps)
        visited |= 1 << (2 * state + cur)
        w, d, ns = table[state][cur]
        if ns == state:
            if d > 0:
                if not right:
                    return "infinite", steps, _ones(left, right), ops, visited, None
                n = right.pop()[1]
                _push(left, w, n)
                steps += n
                continue
            if not left and cur == 0:
                return "infinite", steps, _ones(left, right), ops, visited, None
            if left and left[-1][0] == cur:
                _pop1(right)
                n = left.pop()[1]
                _push(right, w, n + 1)
                _push(right, _pop1(left), 1)
                steps += n + 1
                continue
        _pop1(right)
        if d > 0:
            _push(left, w, 1)
        else:
            _push(right, w, 1)
            _push(right, _pop1(left), 1)
        steps += 1
        state = ns
        if state == HALT:
            return "halt", steps, _ones(left, right), ops, visited, None
        if state == stop_on_entry:
            return "entry", steps, _ones(left, right), ops, visited, (left, right, state, steps)
    return "ops", steps, _ones(left, right), limit, visited, None


def prefix():
    r = run(parse(BASE + "_1RZ1RZ_1RZ1RZ_1RZ1RZ"), 1000000, stop_before=(4, 0))
    assert r[:3] == ("entry", 47176869, 4097), r[:5]
    return r[-1]


def canonical(tm):
    t = parse(tm)
    first = t[4][0][2]
    order = [first] + [i for i in range(5, 8) if i != first]
    mapping = dict(zip(order, range(5, 8)))
    return [[(w, d, mapping.get(s, s)) for w, d, s in t[i]] for i in list(range(5)) + order]


def worker(args):
    wid, seconds, seed, initial_elites, budget, deep_budget = args
    rng = random.Random(seed + 104729 * wid)
    snap = prefix()
    elites = [canonical(t) for t in initial_elites]
    cache = {}
    counts = Counter()
    best, unresolved = {}, {}
    deadline = time.monotonic() + seconds

    def evaluate(t):
        key = fmt(t)
        if key in cache:
            counts["cache_hits"] += 1
            return cache[key]
        r = run(t, budget, snap)[:5]
        counts["evaluations"] += 1
        if r[0] == "ops" and r[1] - snap[3] > 10000:
            r = run(t, deep_budget, snap)[:5]
            counts["deep_evaluations"] += 1
        counts[r[0]] += 1
        cache[key] = r
        if r[0] == "halt":
            if r[1] > 131112087:
                best[key] = r
        elif r[0] == "ops" and r[1] > 10**9:
            unresolved[key] = r
            if len(unresolved) > 50:
                worst = min(unresolved, key=lambda k: unresolved[k][1])
                del unresolved[worst]
        return r

    def entry():
        return (rng.randrange(2), rng.choice((-1, 1)), rng.randrange(8))

    while time.monotonic() < deadline:
        if rng.random() < 0.8:
            table = [row[:] for row in rng.choice(elites)]
        else:
            table = parse(BASE) + [[entry(), entry()] for _ in range(3)]
            table[rng.randrange(5, 8)][rng.randrange(2)] = (1, 1, HALT)
        result = evaluate(table)
        score = result[1] if result[0] == "halt" else 0
        for _ in range(300):
            if time.monotonic() >= deadline:
                break
            cand = [row[:] for row in table]
            for _ in range(1 if rng.random() < 0.9 else 2):
                if rng.random() < 0.05:
                    cand[4][0] = (rng.randrange(2), rng.choice((-1, 1)), 5)
                    continue
                i, j = rng.randrange(5, 8), rng.randrange(2)
                if rng.random() < 0.12:
                    for a in range(5, 8):
                        for b in (0, 1):
                            if cand[a][b][2] == HALT:
                                cand[a][b] = entry()
                    cand[i][j] = (1, rng.choice((-1, 1)), HALT)
                else:
                    if cand[i][j][2] == HALT:
                        continue
                    cand[i][j] = entry()
            cr = evaluate(cand)
            cs = cr[1] if cr[0] == "halt" else 0
            if cs > score or (cs == score and rng.random() < 0.2):
                table, result, score = cand, cr, cs
                counts["accepted"] += 1
        if result[0] == "halt" and score > 131112087:
            elites.append(table)
            elites = sorted(elites, key=lambda t: cache.get(fmt(t), ("halt", 131112087))[1], reverse=True)[:20]
    return {"worker": wid, "counts": dict(counts),
            "best": sorted([[v[1], v[2], k] for k, v in best.items()], reverse=True)[:50],
            "unresolved": sorted([[v[1], v[2], k] for k, v in unresolved.items()], reverse=True)[:20]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seconds", type=int, default=180)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--seed", type=int, default=20260926)
    p.add_argument("--ops", type=int, default=3000)
    p.add_argument("--deep-ops", type=int, default=300000)
    p.add_argument("--output", default="run3_20260926.json")
    a = p.parse_args()
    prior = json.load(open("run2_merged.json"))
    base = parse(BASE)
    elites = [t for _, _, t in prior["best"] if len(parse(t)) == 8
              and parse(t)[:4] == base[:4] and parse(t)[4][1] == base[4][1]
              and parse(t)[4][0][2] in (5, 6, 7)]
    start = time.monotonic()
    with mp.Pool(a.workers) as pool:
        results = pool.map(worker, [(w, a.seconds, a.seed, elites, a.ops, a.deep_ops) for w in range(a.workers)])
    best = {t: (s, o, t) for r in results for s, o, t in r["best"]}
    out = {"configuration": vars(a), "elapsed_seconds": time.monotonic() - start,
           "best": sorted(best.values(), reverse=True), "workers": results}
    with open(a.output, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({"elapsed": out["elapsed_seconds"], "best": out["best"][:10],
                      "counts": [r["counts"] for r in results]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
