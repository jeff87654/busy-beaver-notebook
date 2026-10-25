"""Candidate table for RESULTS.md from cand/*.json + *.val."""
import json, re, sys, subprocess
rows = []
for name, track, change in [l.split('|') for l in open('cand/LIST').read().strip().splitlines()]:
    c = json.load(open(f'cand/{name}.json')); v = open(f'cand/{name}.val').read()
    cc = subprocess.run(['python', 'constants.py', f'cand/{name}.tm'], capture_output=True, text=True).stdout
    tot = re.search(r'states (\d+) \(framework (\d+), DAG (\d+)\)', cc)
    mm = re.search(r'ops compared (\d+) mismatches (\d+)', v)
    sm = re.search(r'semtest \S+ trials (\d+) mismatches (\d+)', v)
    st = re.search(r'accelerated nodes \d+ cases \d+ mismatches (\d+)', v)
    car = re.search(r'max car run (\d+); max depth (\d+); max break (\d+)', cc)
    ip = re.search(r'prefix ops (\d+)', v)
    rows.append(f'| `{name}.tm` | **{tot.group(1)}** | {tot.group(2)}+{tot.group(3)} | {track} | {change} | '
                f'{mm.group(1)} ops / {mm.group(2)} | {sm.group(1)} / {sm.group(2)} (selftest {st.group(1)}) | '
                f'{car.group(1)} / {car.group(2)} / {car.group(3)} / {ip.group(1)} |')
print('| file | states | framework+DAG | track | changes (cumulative) | TM-vs-RM crosscheck: ops / mismatches | '
      'semantic test: trials / mismatches | max car run / max depth / max break / IP prefix ops |')
print('|---|---|---|---|---|---|---|---|')
print('| `ext/.../zf2.tm` (Wade) | 393 | 69+324 | - | original | 2527 / 0 | 1500 / 0 | 9 / 136 / 2 / 358 |')
print('\n'.join(rows))
