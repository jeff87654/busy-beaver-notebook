"""Re-grade the fitted rows of a finished scan with the final dlscan3.exe (the scan's chunks were run with several
detector versions; the census and templates are identical across them, so only machines with an R1-R3 fit can change).

  python regrade.py SCANDIR [NPROC] [CENSUS]

Writes SCANDIR/regraded.tsv (all fitted rows, final grades) and SCANDIR/regraded_summary.txt.
"""
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
IDLE = 0x00000040


def main():
    d = Path(sys.argv[1])
    nproc = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    census = sys.argv[3] if len(sys.argv) > 3 else '1000000'
    ms = []
    for f in sorted((d / 'out').glob('*.tsv')):
        for line in open(f):
            if line.startswith('machine\t') or line.startswith('#') or not line.strip():
                continue
            ms.append(line.split('\t')[0])
    ms = sorted(set(ms))
    work = d / 'regrade'
    work.mkdir(exist_ok=True)
    parts = [ms[i::nproc] for i in range(nproc)]
    procs = []
    for i, p in enumerate(parts):
        if not p:
            continue
        inp = work / f'r_{i}.txt'
        inp.write_text('\n'.join(p) + '\n')
        out = work / f'r_{i}.tsv'
        err = open(work / f'r_{i}.err', 'w')
        procs.append((subprocess.Popen([str(HERE / 'dlscan3.exe'), str(inp), str(out), census, '20000'],
                                       stdout=err, stderr=err, creationflags=IDLE), out, err))
    rows = []
    for p, out, err in procs:
        p.wait()
        err.close()
        for line in open(out):
            if line.startswith('machine\t') or line.startswith('#') or not line.strip():
                continue
            rows.append(line.rstrip('\n'))
    order = ['W1-HALTER', 'W1-HALT?', 'W1-LOOPER', 'MULTI', 'MULTI?', 'LOOPER', 'REBUILD', 'CHAMPION', 'R4-SOME',
             'HALT?', 'HALT-SOME', 'CHECK', 'NOBOUNDARY', 'SAFE']
    rows.sort(key=lambda r: order.index(r.split('\t')[3]) if r.split('\t')[3] in order else 99)
    with open(d / 'regraded.tsv', 'w') as fh:
        fh.write('machine\thalted_step\tn_templates\tgrade\ttemplate\tw1\tparams\n')
        fh.write(''.join(r + '\n' for r in rows))
    c = Counter(r.split('\t')[3] for r in rows)
    (d / 'regraded_summary.txt').write_text(f'fitted {len(ms)}: ' + ', '.join(f'{k} {c[k]}' for k in order if c.get(k)) + '\n')
    print(d, len(ms), dict(c))


if __name__ == '__main__':
    main()
