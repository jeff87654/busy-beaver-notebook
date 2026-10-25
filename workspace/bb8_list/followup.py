"""Follow-up stage: pick prominent holdouts from the 2-CPU-second ranking and characterize their growth.

Calibration on BB(7) (2/10/40 CPU-second budgets, persistent Quick_Sim workers):
  champion 1RB0RA_...: 1,872 -> 6,850 -> 14,397 digits; digits per loop 0.84 -> 1.77 -> 2.26 (rising)
  fast exponential growers: ~450 -> ~2,300 -> ~7,000 digits; digits per loop 0.018, flat
Plain exponential growers add a small constant number of digits per simulator loop. Machines
driven by a nonlinear (e.g. doubling) proven rule approach Quick_Sim's cap: general rules are
applied at most --max-num-reps = 10 times per loop, so a doubling rule gives <= 10*log10(2) ~ 3.01
digits per loop. The BB(7) champion is in this "doubling" class, but so are non-halters: the
control investigation (investigations/bb7_control_16582.md) proved a doubling-class BB(7) holdout
nonhalting. Digits per loop therefore cannot separate nested halters from doubling non-halters.
Doubling-class machines need real analysis.

Pipeline (restartable; state in followup/state.json):
  select : score2 (digits at 2 CPU-s) >= 100, or halted with >= 10 digits;
           exact duplicates of (score2, loops2, rules) are grouped under one representative
  stage A: rerun at 10 CPU-s     -> dpl10, accel10 = dpl10 / dpl2
  stage B: if dpl10 >= 0.2: rerun at 40 CPU-s -> dpl40, accel40 = dpl40 / dpl2
  class  : halted (exact sigma) | infinite (prover) | doubling (dpl40 >= 0.5, near the ~3.01 cap)
           | exponential (dpl10 < 0.2) | other
Outputs followup/promising.tsv (doubling-class and big halters) and followup/all.tsv.
Run under the venv interpreter at Idle priority:
  ../third_party/venv311/Scripts/python.exe followup.py [--once] [--jobs-glob 'jobs8/*']
"""
from __future__ import annotations

import argparse
import glob
import json
import time
from pathlib import Path

import fast_rank

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'followup'


def digits(r):
    o = (r or {}).get('ones') or {}
    k = o.get('kind')
    if k == 'integer':
        return len(o['decimal'])
    if k == 'large_integer':
        return round(o['bit_length'] * 0.30103)
    if k == 'symbolic_expression':
        return 10**9
    return -1


def dpl(r):
    loops = (r or {}).get('loops') or 0
    return digits(r) / loops if loops else 0.0


def load_state():
    p = OUT / 'state.json'
    return json.loads(p.read_text()) if p.exists() else {}


def save_state(state):
    OUT.mkdir(exist_ok=True)
    tmp = OUT / 'state.partial.json'
    tmp.write_text(json.dumps(state, indent=1))
    tmp.replace(OUT / 'state.json')


def scan(jobs_glob):
    rows = []
    for f in glob.glob(str(ROOT / jobs_glob / 'growth' / '*.json')):
        if f.endswith('.partial.json'):
            continue
        job = Path(f).parent.parent.name
        for r in json.loads(Path(f).read_text())['results']:
            r['_job'] = job
            rows.append(r)
    return rows


def classify(e):
    if e.get('halted'):
        return 'halted'
    if e.get('infinite'):
        return 'infinite'
    if e.get('dpl40', 0) >= 0.5:
        return 'doubling'
    if 'dpl10' in e and e['dpl10'] < 0.2:
        return 'exponential'
    return 'other' if 'dpl10' in e else 'pending'


def summarize(r):
    return {'digits': digits(r), 'loops': r.get('loops'), 'reason': r.get('reason'),
            'cpu': round(r.get('elapsed_seconds') or 0, 2), 'steps': r.get('steps'), 'ones': r.get('ones')}


def run_budget(machines, T, workers):
    if not machines:
        return {}
    pool = fast_rank.Pool(workers=workers, sim_time=T, hard_timeout=5 * T + 60)
    try:
        return {r['machine']: r for r in pool.rank(machines)}
    finally:
        pool.close()


def step(state, jobs_glob, workers):
    rows = scan(jobs_glob)
    groups = {}
    for r in rows:
        d = digits(r)
        halted = r.get('status') in ('undefined', 'halt')
        if not (d >= 100 or (halted and d >= 10)):
            continue
        key = f"{d}|{r.get('loops')}|{r.get('rules_proven')}|{r.get('reason')}"
        groups.setdefault(key, []).append(r)
    new = 0
    for key, members in groups.items():
        rep = min(members, key=lambda r: r['machine'])
        e = state.setdefault(rep['machine'], {'job': rep['_job'], 'score2': digits(rep), 'r2': summarize(rep)})
        e['variants'] = sorted({m['machine'] for m in members} - {rep['machine']})
        if rep.get('status') in ('undefined', 'halt'):
            e['halted'] = True
        if str(rep.get('reason', '')).startswith('INF'):
            e['infinite'] = True
        new += 'class' not in e
    todo_a = [m for m, e in state.items() if 'dpl10' not in e and not e.get('halted') and not e.get('infinite')]
    for m, r in run_budget(todo_a, 10, workers).items():
        e = state[m]
        e['r10'] = summarize(r)
        e['dpl2'] = dpl(e['r2'])
        e['dpl10'] = dpl(r)
        e['accel10'] = e['dpl10'] / e['dpl2'] if e['dpl2'] else 0.0
        if r.get('status') in ('undefined', 'halt'):
            e['halted'] = True
        if str(r.get('reason', '')).startswith('INF'):
            e['infinite'] = True
    save_state(state)
    todo_b = [m for m, e in state.items() if 'dpl40' not in e and not e.get('halted') and not e.get('infinite')
              and e.get('dpl10', 0) >= 0.2]
    for m, r in run_budget(todo_b, 40, workers).items():
        e = state[m]
        e['r40'] = summarize(r)
        e['dpl40'] = dpl(r)
        e['accel40'] = e['dpl40'] / e['dpl2'] if e.get('dpl2') else 0.0
        if r.get('status') in ('undefined', 'halt'):
            e['halted'] = True
            e['r_halt'] = summarize(r)
    for e in state.values():
        e['class'] = classify(e)
    save_state(state)
    write_tables(state)
    return new, len(todo_a), len(todo_b)


def write_tables(state):
    order = {'doubling': 0, 'halted': 1, 'other': 2, 'exponential': 3, 'pending': 4, 'infinite': 5}

    def key(item):
        m, e = item
        best = max(e.get('r40', {}).get('digits', -1), e.get('r10', {}).get('digits', -1), e['score2'])
        return (order.get(e['class'], 9), -best)
    head = 'class\tjob\tscore2\td10\td40\tdpl2\tdpl10\tdpl40\taccel40\tvariants\tmachine'
    lines = []
    for m, e in sorted(state.items(), key=key):
        lines.append('\t'.join(str(x) for x in (
            e['class'], e['job'], e['score2'], e.get('r10', {}).get('digits', ''), e.get('r40', {}).get('digits', ''),
            f"{e.get('dpl2', 0):.3f}", f"{e.get('dpl10', 0):.3f}" if 'dpl10' in e else '',
            f"{e.get('dpl40', 0):.3f}" if 'dpl40' in e else '', f"{e.get('accel40', 0):.2f}" if 'accel40' in e else '',
            len(e.get('variants', [])), m)))
    (OUT / 'all.tsv').write_text(head + '\n' + '\n'.join(lines) + '\n')
    prom = [l for l in lines if l.split('\t')[0] in ('doubling', 'halted')]
    (OUT / 'promising.tsv').write_text(head + '\n' + '\n'.join(prom) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs-glob', default='jobs8/*')
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--once', action='store_true')
    ap.add_argument('--every', type=float, default=1800, help='seconds between scans')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    state = load_state()
    while True:
        new, na, nb = step(state, a.jobs_glob, a.workers)
        counts = {}
        for e in state.values():
            counts[e['class']] = counts.get(e['class'], 0) + 1
        print(time.strftime('%H:%M:%S'), f'{new} new groups; stage A {na}, stage B {nb}; classes {counts}', flush=True)
        if a.once:
            break
        time.sleep(a.every)


if __name__ == '__main__':
    main()
