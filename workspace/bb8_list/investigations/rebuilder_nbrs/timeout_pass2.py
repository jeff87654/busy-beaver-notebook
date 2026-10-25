"""Two-stage template fit for machines on which a full dlscan2 run is too slow.

  python timeout_pass2.py infer GRADED.tsv OUT.tsv [WORKERS=3]
      TIMEOUT rows of GRADED.tsv (grade_timeout.py output) with in_m8 = 0: list dlscan2's inferred templates
      (`--all`, N = 1, timeout 180 s) and fit those whose unit has length >= 2.
  python timeout_pass2.py fixed SINGLES.tsv OUT.tsv [WORKERS=3]
      TIMEOUT rows of SINGLES.tsv (tmpl_scan.py output): fit the parent's own template.

Each template is fitted with `dlscan2 --tmpl` at N = 5000 first (timeout 20 s).  A genuine champion-type
machine passes its R1-R3 probes within a few thousand steps (R1 at b = 5 takes about 1800), so a failure
there rejects the template; only templates that pass are refitted at the usual N = 100000 (timeout 180 s).
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tmpl_scan import TEMPLATES, RULES

HERE = Path(__file__).resolve().parent
EXE = (HERE / '..' / '..' / 'neighbors' / 'dlscan2.exe').resolve()
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
ORDER = ['CHAMPION', 'R4-SOME', 'HALT?', 'HALT-SOME', 'CHECK', 'NOBOUNDARY', 'SAFE']
TRX = re.compile(r'([LR]),([A-H]),P=([01]*),u=([01]+),s=([01]+),d=(\d+)d\+(\d+),b=(\d+)b\+(\d+),S=([01-]*)$')


def list_templates(m, td):
    i, o = Path(td) / f'{threading.get_ident()}.txt', Path(td) / f'{threading.get_ident()}.tsv'
    i.write_text(m + '\n')
    try:
        subprocess.run([str(EXE), str(i), str(o), '5000000', '1', '--all'], creationflags=LOW, timeout=180,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return None
    rows = [l.split('\t') for l in o.read_text().splitlines()[1:] if not l.startswith('#')]
    if not rows or rows[0][-1] == '-':
        return []
    out = []
    for t in rows[0][-1].split(';'):
        g = TRX.match(t)
        if g and len(g.group(4)) >= 2:
            o_, q, P, u, s, al, be, alB, beB, S = g.groups()
            out.append([o_, q, P or '-', u, s, al, be, alB, beB, S or '-'])
    return out


def fit(m, targs, n, timeout):
    try:
        r = subprocess.run([str(EXE), '--tmpl', m, *targs, str(n)], creationflags=LOW, timeout=timeout,
                           capture_output=True, text=True)
    except subprocess.TimeoutExpired:
        return 'TIMEOUT', '-'
    last = [l for l in r.stdout.splitlines() if l.startswith('fit ')]
    mm = re.match(r'fit ok=(\d) grade=(\S+) ?(.*)', last[0]) if last else None
    if not mm or mm.group(1) != '1':
        return '-', '-'
    return mm.group(2), mm.group(3)


def two_stage(m, tmpls):
    best, n_stage1_to, n_pass1 = None, 0, 0
    for t in tmpls:
        g, p = fit(m, t, 5000, 20)
        if g == 'TIMEOUT':
            n_stage1_to += 1
            continue
        if g == '-':
            continue
        n_pass1 += 1
        g, p = fit(m, t, 100000, 180)
        if g in ('-', 'TIMEOUT'):
            continue
        if best is None or ORDER.index(g) < ORDER.index(best[0]):
            best = (g, ','.join(t), p)
    return n_stage1_to, n_pass1, best


def main():
    mode, src, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    rows = [l.split('\t') for l in src.read_text().splitlines()[1:]]
    if mode == 'infer':
        todo = [r for r in rows if r[6] == 'TIMEOUT' and r[3] == '0']
    else:
        todo = [r for r in rows if r[3] == 'TIMEOUT']
    lock = threading.Lock()
    with tempfile.TemporaryDirectory() as td, out.open('w') as f, ThreadPoolExecutor(workers) as ex:
        f.write('machine\tinfo\tn_templates\tn_stage1_timeouts\tn_pass_stage1\tgrade\ttemplate\tparams\trules_same\n')

        def job(r):
            m = r[0]
            if mode == 'infer':
                tm = list_templates(m, td)
                info = f'p{r[1]}:{r[2]}'
            else:
                tm = [TEMPLATES[int(r[1])]]
                info = f'p{r[1]}:{r[2]}'
            if tm is None:
                res = ['LIST-TIMEOUT', '-', '-', '-', '-', '-', '-']
            else:
                to, n1, best = two_stage(m, tm)
                g, t, p = best if best else ('-', '-', '-')
                res = [str(len(tm)), str(to), str(n1), g, t, p, str(int(p.startswith(RULES)))]
            with lock:
                f.write('\t'.join([m, info] + res) + '\n')
                f.flush()
        list(ex.map(job, todo))
    print(f'done: {len(todo)} machines -> {out}')


if __name__ == '__main__':
    main()
