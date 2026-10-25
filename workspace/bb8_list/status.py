"""Summarize BB(8) list progress:  python status.py"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEAN_NODES_PER_JOB = 4.3e9  # Knuth estimate of the mean 8-state subtask (4.3e15 / 1e6); jobs vary widely

for jobdir in sorted((ROOT / 'jobs8').glob('*')):
    info = jobdir / 'job.json'
    if info.exists():
        j = json.loads(info.read_text())
        rank = jobdir / 'ranking.tsv'
        top = rank.read_text().splitlines()[1:2] if rank.exists() else []
        print(f"{jobdir.name}: COMPLETE  {j['nodes']:.3g} nodes, {j['holdouts']} holdouts, "
              f"{j['cpu_seconds']/3600:.1f} CPU-h; ranking: {'done, top: ' + top[0] if top else 'pending'}")
        continue
    seed = jobdir / 'seed' / 'seed_stats.json'
    nodes = json.loads(seed.read_text())['nodes_started'] if seed.exists() else 0
    cpu = json.loads(seed.read_text())['elapsed_seconds'] if seed.exists() else 0
    hold = 0
    for st in (jobdir / 'results').glob('*_stats.json') if (jobdir / 'results').exists() else []:
        s = json.loads(st.read_text())
        nodes += s['nodes_started']
        cpu += s['elapsed_seconds']
        h = st.with_name(st.name.replace('_stats.json', '_holdouts.txt'))
        hold += sum(1 for l in h.read_text().splitlines() if '_' in l)
    pend = len(list((jobdir / 'chunks' / 'pending').glob('*.txt'))) if (jobdir / 'chunks').exists() else '?'
    done = len(list((jobdir / 'chunks' / 'done').glob('*.txt'))) if (jobdir / 'chunks' / 'done').exists() else 0
    print(f"{jobdir.name}: RUNNING   chunks done {done}, pending {pend}; {nodes:.3g} nodes "
          f"(~{100*nodes/MEAN_NODES_PER_JOB:.1f}% of an average job), {hold} holdouts so far, "
          f"{cpu/3600:.1f} CPU-h in accepted chunks")

state_file = ROOT / 'followup' / 'state.json'
if state_file.exists():
    st = json.loads(state_file.read_text())
    counts = {}
    for e in st.values():
        counts[e.get('class', '?')] = counts.get(e.get('class', '?'), 0) + 1
    prom = [l for l in (ROOT / 'followup' / 'promising.tsv').read_text().splitlines()[1:] if l.strip()] \
        if (ROOT / 'followup' / 'promising.tsv').exists() else []
    print(f"follow-up: {len(st)} prominent groups {counts}; promising (doubling-class or big halt): {len(prom)}")
    for l in prom[:5]:
        print('  ' + l)
inv = ROOT / 'investigations'
if inv.exists():
    print('investigations:', ', '.join(p.stem for p in sorted(inv.glob('*.md'))) or 'none yet')

pf = ROOT / 'prefilter_results.json'
if pf.exists():
    res = json.loads(pf.read_text())
    n_ok = sum(1 for r in res.values() if r['status'] == 'verified_nonhalting')
    print(f"pre-filter (mxdys verified deciders): {n_ok} of {len(res)} doubling machines decided non-halting; "
          f"{len(res) - n_ok} left for investigators")

if (ROOT / 'neighbors' / 'dlscan_all.py').exists():
    import sys
    sys.path.insert(0, str(ROOT / 'neighbors'))
    import dlscan_all
    print(dlscan_all.status_line())
if (ROOT / 'neighbors' / 'dlscan2_all.py').exists():
    import dlscan2_all
    print(dlscan2_all.status_line())
