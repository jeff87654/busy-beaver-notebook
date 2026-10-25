"""nhms.py: exact steps/ones (ms.exe macro sim) for the nhrun halters."""
import idle  # noqa
import subprocess, os, sys
from concurrent.futures import ThreadPoolExecutor
MS = os.path.abspath('../reb7/grows/ms.exe')
Ks = [5, 4, 3]
jobs = []
for i in range(3):
    for l in open(f'nh/out{i}.tsv'):
        p = l.rstrip('\n').split('\t')
        if len(p) > 3 and p[-1] == 'HALT': jobs.append((i, p[0], Ks[i]))
def run(j):
    i, m, K = j
    pr = subprocess.Popen([MS, m, str(K), '300000000', '0'], stdout=subprocess.PIPE, text=True)
    open('pids.txt', 'a').write(f'nhms child={pr.pid}\n')
    out = pr.communicate()[0].strip().splitlines()
    return f'{i}\t{m}\t{out[-1] if out else "?"}'
with ThreadPoolExecutor(2) as ex:
    res = list(ex.map(run, jobs))
open('nh/ms.tsv', 'w').write('\n'.join(res) + '\n')
