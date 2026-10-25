"""Cheap automated pre-filter before spending an investigation: mxdys's verified deciders, deeper settings.

Runs a portfolio of mxdys MitM_CTL deciders (NG / RWL_mod / CPS_LRU families) in `exec` mode. That is
the path where upstream's closure verifier (CTL_Fixedlen_verify) re-checks every certificate. The
8-state binary is ../candidate_deciders_deep_verified.exe (upstream deciders, 256-bit words). A
success is replayed in a fresh process before it counts. Results are C++-verifier-checked, not Coq.
Each attempt has a short time limit and runs at Idle priority.

  python prefilter.py --machines M1 M2 ... [--out prefilter_results.json] [--workers 2]
  python prefilter.py --promising            # all undispatched doubling rows in followup/promising.tsv
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXE = ROOT.parent / 'candidate_deciders_deep_verified.exe'
RUNS = ROOT / 'prefilter_runs'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
PORTFOLIO = [
    'chr_LRUH 0 chr_H 0 MitM_CTL NG maxT 300000 NG_n 6 run',
    'chr_LRUH 32 chr_H 24 MitM_CTL NG maxT 300000 NG_n 4 run',
    'chr_LRUH 48 chr_H 32 MitM_CTL NG maxT 300000 NG_n 3 run',
    'chr_LRUH 16 chr_H 12 MitM_CTL NG maxT 300000 NG_n 6 run',
    'MitM_CTL RWL_mod sim 1001 maxT 300000 H 8 mod 4 n 2 run',
    'MitM_CTL RWL_mod sim 1001 maxT 300000 H 6 mod 3 n 3 run',
    'MitM_CTL CPS_LRU sim 1001 maxT 300000 LRUH 16 H 2 tH 2 n 3 run',
    'MitM_CTL CPS_LRU sim 1001 maxT 300000 LRUH 8 H 1 tH 1 n 4 run',
]
ENV = dict(os.environ)
ENV['PATH'] = r'C:\msys64\ucrt64\bin;' + ENV.get('PATH', '')
for k in [k for k in ENV if k.startswith('BB_PILOT_')]:
    ENV.pop(k)


def attempt(machine, p, tag, timeout):
    d = RUNS / f'{machine.replace("-", "x")}_{p:02d}{tag}'
    d.mkdir(parents=True, exist_ok=True)
    enc = machine.replace('1RZ', '---')
    (d / 'input.txt').write_text(f'{enc} {PORTFOLIO[p]}\n')
    t = time.monotonic()
    try:
        r = subprocess.run([str(EXE), 'exec', 'input.txt'], cwd=d, env=ENV, capture_output=True, text=True,
                           timeout=timeout, creationflags=LOW)
        log = (d / 'log.txt').read_text() if (d / 'log.txt').exists() else ''
        if r.returncode:
            status = 'error'
        elif f'{enc} N' in log:
            status = 'verified_nonhalting'
        elif f'{enc} H' in log:
            status = 'halting'
        else:
            status = 'unresolved'
    except subprocess.TimeoutExpired:
        status = 'timeout'
    return status, round(time.monotonic() - t, 2)


def decide(machine, timeout):
    tries = []
    for p in range(len(PORTFOLIO)):
        status, secs = attempt(machine, p, '', timeout)
        tries.append({'config': p, 'status': status, 'seconds': secs})
        if status == 'verified_nonhalting':
            replay, _ = attempt(machine, p, '_replay', timeout)
            if replay == 'verified_nonhalting':
                return {'machine': machine, 'status': 'verified_nonhalting', 'config': PORTFOLIO[p], 'tries': tries}
        if status == 'halting':
            return {'machine': machine, 'status': 'halting', 'config': PORTFOLIO[p], 'tries': tries}
    return {'machine': machine, 'status': 'unresolved', 'tries': tries}


def promising_undispatched():
    disp = {l.split('\t')[0] for l in (ROOT / 'investigations' / 'dispatched.txt').read_text().splitlines() if l.strip()}
    rows = [l.split('\t') for l in (ROOT / 'followup' / 'promising.tsv').read_text().splitlines()[1:] if l.strip()]
    return [r[-1] for r in rows if r[0] == 'doubling' and r[-1] not in disp]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--machines', nargs='*', default=[])
    ap.add_argument('--promising', action='store_true')
    ap.add_argument('--out', default=str(ROOT / 'prefilter_results.json'))
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--timeout', type=float, default=8.0)
    a = ap.parse_args()
    machines = [m.strip() for m in a.machines if m.strip()] + (promising_undispatched() if a.promising else [])
    out = Path(a.out)
    done = json.loads(out.read_text()) if out.exists() else {}
    todo = [m for m in dict.fromkeys(machines) if m not in done]
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for res in pool.map(lambda m: decide(m, a.timeout), todo):
            done[res['machine']] = res
            out.write_text(json.dumps(done, indent=1))
            print(res['status'], res.get('config', ''), res['machine'], flush=True)


if __name__ == '__main__':
    main()
