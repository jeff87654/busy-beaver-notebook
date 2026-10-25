"""Differential test of dlscan.exe's probe against the Python tools (kfam.run_next).

  python test_dlscan.py KEYS.tsv [N=20000] [max_machines=150]
KEYS.tsv is a `dlscan ... --all` output (its last column lists every candidate key). For each machine and key,
the probes K(2;2;b), K(2;0;b), K(1,2,0;0;b), K(1,2,0,0;0;b), K(;0;b) (b = 1..3) are run by both and compared.
"""
import os
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'investigations' / 'neighbors_family_tools'))
import kfam  # noqa: E402


def mirror(tm):
    return tm.translate(str.maketrans('LR', 'RL'))


def main():
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 150
    rows = [l.split('\t') for l in Path(sys.argv[1]).read_text().splitlines()[1:] if not l.startswith('#')]
    random.Random(1).shuffle(rows)
    cases = []
    for f in rows[:cap]:
        for key in ([] if f[5] == '-' else f[5].split(';')):
            o, q, suf, u, sep = key.split(',')
            tm = mirror(f[0]) if o == 'L' else f[0]
            for ds, a in (((2,), 2), ((2,), 0), ((1, 2, 0), 0), ((1, 2, 0, 0), 0), ((), 0)):
                for b in (1, 2, 3):
                    cases.append((tm, q, suf, u, sep, ds, a, b))
    inp = HERE / 'test_dlscan_cases.txt'
    inp.write_text(''.join(f"{tm} {q} {suf} {u} {sep} {','.join(map(str, ds)) or '-'} {a} {b}\n"
                           for tm, q, suf, u, sep, ds, a, b in cases), newline='\n')
    got = subprocess.run([os.environ.get('DLSCAN_EXE', str(HERE / 'dlscan.exe')), '--probe', str(inp), str(N)], capture_output=True, text=True,
                         check=True).stdout.splitlines()
    assert len(got) == len(cases), (len(got), len(cases))
    bad = 0
    kinds = {}
    for c, g in zip(cases, got):
        tm, q, suf, u, sep, ds, a, b = c
        kfam.ENC = (u, sep)
        r = kfam.run_next(tm, ds, a, b, N=N, shape=(q, suf))
        if r[0] == 'K':
            exp = 'K %d %s|%d|%d' % (r[1], ','.join(map(str, r[2][0])), r[2][1], r[2][2])
        elif r[0] == 'HALT':
            exp = 'HALT %d' % r[1]
        else:
            exp = 'TIMEOUT'
        kinds[r[0]] = kinds.get(r[0], 0) + 1
        if exp != g:
            bad += 1
            if bad <= 10:
                print('MISMATCH', c, 'python:', exp, 'c++:', g)
    inp.unlink()
    print(f'{len(cases)} probes compared, {bad} mismatches; python outcomes {kinds}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
