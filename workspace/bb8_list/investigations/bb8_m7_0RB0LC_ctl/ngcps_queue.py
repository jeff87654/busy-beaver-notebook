"""ngcps_queue.py MACHINES.txt [BUDGET_S=600]: automatic n-gram closed-position-set proofs for a list of 8-state machines.

For each machine: try ngcps2.exe over window pairs (nL, nR) in increasing total size (each run <= 120 s, at most
BUDGET_S per machine); on NONHALT dump the certificate, generate proofs/BB8_ng_<machine>.v with gen_ngcps_any.py and
run check.py on it. Everything runs at Idle priority. One line per machine is appended to ngcps_results.tsv:
  machine  verdict(PASS/FAIL/OPEN/BUDGET)  nL/nR  configs  proof-file  seconds
A PASS line is check.py's verdict (statement, table and "Closed under the global context" checked by Coq).
Machines already PASSed in ngcps_results.tsv are skipped.
"""
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROOFS = HERE.parent.parent / 'proofs'
PY = r'C:\Users\jeffr\Downloads\bb8\third_party\venv311\Scripts\python.exe'
EXE = HERE / 'ngcps2.exe'
LOW = 0x40  # IDLE_PRIORITY_CLASS
RES = HERE / 'ngcps_results.tsv'
CERTS = HERE / 'certs'
CERTS.mkdir(exist_ok=True)
import os
MAXW = int(os.environ.get('NG_MAX_W', 16))           # largest window length tried (keys hold up to 30)
RUN_T = int(os.environ.get('NG_RUN_TIMEOUT', 120))    # seconds per ngcps2 run
PAIRS = sorted({(a, b) for a in range(4, MAXW + 1) for b in range(4, MAXW + 1)}, key=lambda p: (p[0] + p[1], abs(p[0] - p[1]), p))


def search(m, budget):
    t0 = time.time()
    for a, b in PAIRS:
        if time.time() - t0 > budget:
            return 'BUDGET', None
        try:
            r = subprocess.run([str(EXE), m, str(a), str(b)], capture_output=True, text=True, timeout=RUN_T, creationflags=LOW)
        except subprocess.TimeoutExpired:
            continue
        if r.stdout.startswith('NONHALT'):
            n = int(re.search(r': (\d+) configs', r.stdout).group(1))
            return 'NONHALT', (a, b, n)
    return 'OPEN', None


def main():
    machines = [l.split()[0] for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    done = set()
    if RES.exists():
        done = {l.split('\t')[0] for l in RES.read_text().splitlines() if '\tPASS\t' in l}
    for m in machines:
        if m in done or len(m.split('_')) != 8:
            continue
        t0 = time.time()
        verdict, info = search(m, budget)
        name, nlnr, nconf = '-', '-', '-'
        if verdict == 'NONHALT':
            a, b, n = info
            nlnr, nconf = f'{a}/{b}', str(n)
            tag = m.replace('_', '').replace('---', 'xxx')
            cert = CERTS / f'{tag}_{a}_{b}.txt'
            subprocess.run([str(EXE), m, str(a), str(b), str(cert)], capture_output=True, text=True,
                           env={**__import__('os').environ, 'NOC': '1'}, creationflags=LOW)
            name = f'BB8_ng_{tag}.v'
            subprocess.run([PY, str(HERE / 'gen_ngcps_any.py'), m, str(cert), str(PROOFS / name), str(n)], check=True,
                           capture_output=True, text=True)
            for attempt in (1, 2):   # one retry: a first check.py run once failed transiently after a good compile
                r = subprocess.run([PY, 'check.py', name], cwd=PROOFS, capture_output=True, text=True, creationflags=LOW)
                with open(HERE / 'ngcps_check.log', 'a') as lf:
                    lf.write(f'=== {name} attempt {attempt}\n{r.stdout}{r.stderr[-3000:]}\n')
                verdict = 'PASS' if r.stdout.startswith('PASS') else 'FAIL'
                if verdict == 'PASS':
                    break
        line = '\t'.join([m, verdict, nlnr, nconf, name, f'{time.time() - t0:.0f}'])
        print(line, flush=True)
        with open(RES, 'a') as f:
            f.write(line + '\n')


if __name__ == '__main__':
    main()
