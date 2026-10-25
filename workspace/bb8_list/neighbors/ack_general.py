"""Generalized Ackermann-style (digit-list) scan: infer the digit encoding from tape snapshots, then test it.

The base scan (scan_ack.py) only knows digits written as 1^d separated by single 0s. Here a digit d may be
unit^d with any short unit starting with '1' (e.g. '10', '110'), separated by any short separator
(e.g. '11', '00').
1. stage1.exe dumps right-end tape snapshots per machine (5e6 literal steps, C++).
2. For each (state, suffix, unit, sep), count the snapshots that parse into >= 3 digits, at least two of them
   >= 2 and not all equal. Keep the 3 best keys seen in >= 2 snapshots. The base encoding (1, 0) is skipped,
   since scan_ack.py covers it.
3. Run kfit.py under BB_KENC=unit,sep with --shape state,suffix. A machine whose count-down (R1), reset (R2)
   and zero-digit refill (R3) rules all fit on constructed configurations is a digit-list counter.

  python ack_general.py machines.txt out.tsv
"""
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent / 'investigations' / 'neighbors_family_tools'
STAGE1 = HERE / 'stage1.exe'
PARENT = '1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
UNITS = ['1', '10', '11', '100', '101', '110', '111', '1000', '1010', '1100', '1110']
SEPS = ['0', '1', '00', '01', '10', '11', '000', '001', '011', '100', '110']


def parse_runs(word, u, sep):
    runs, w = [], word
    while True:
        k = 0
        while w.endswith(u):
            w = w[:-len(u)]
            k += 1
        runs.append(k)
        if not w or set(w) == {'0'}:
            break
        if not w.endswith(sep):
            return None
        w = w[:-len(sep)]
        if not w or set(w) == {'0'}:
            runs.append(0)
            break
    runs.reverse()
    return runs


def candidates(snaps):
    score = Counter()
    for q, w in snaps:
        seen = set()
        for L in (1, 2, 3):
            if len(w) <= L:
                continue
            suf, body = w[-L:], w[:-L]
            for u in UNITS:
                for sep in SEPS:
                    if (u, sep) == ('1', '0') or sep == u or (sep.strip('0') == '' and u == '1' and len(sep) > 1 and False):
                        continue
                    runs = parse_runs(body, u, sep)
                    if not runs or len(runs) < 3 or sum(r >= 2 for r in runs) < 2 or len(set(runs)) < 2:
                        continue
                    key = (q, suf, u, sep)
                    if key not in seen:
                        seen.add(key)
                        score[key] += 1
    return [k for k, c in score.most_common() if c >= 2][:3]


def fit(m, key):
    q, suf, u, sep = key
    env = dict(os.environ, BB_KENC=f'{u},{sep}')
    try:
        r = subprocess.run([sys.executable, str(TOOLS / 'kfit.py'), m, '--shape', f'{q},{suf}', '--N', '1000000'],
                           cwd=TOOLS, capture_output=True, text=True, timeout=60, env=env, creationflags=LOW)
    except subprocess.TimeoutExpired:
        return None
    line = next((l for l in r.stdout.splitlines() if l.strip().startswith('R1:')), '')
    parts = [p.strip() for p in line.split('|')]
    ok = lambda tag: any(p.startswith(tag) and 'no fit' not in p for p in parts)
    return line.strip() if ok('R1:') and ok('R2:') and ok('R3:') else None


def main():
    src, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    census, snaps_path = HERE / (src.stem + '_gcensus.tsv'), HERE / (src.stem + '_snaps.tsv')
    env = dict(os.environ, PATH=r'C:\msys64\ucrt64\bin;' + os.environ.get('PATH', ''))
    subprocess.run([str(STAGE1), PARENT, str(src), str(census), '5000000', str(snaps_path)],
                   env=env, creationflags=LOW, check=True, stderr=subprocess.DEVNULL)
    snaps = defaultdict(list)
    for l in snaps_path.read_text().splitlines():
        m, q, w = l.split('\t')
        snaps[m].append((q, w))
    def scan(m):
        hits = []
        for key in candidates(snaps.get(m, [])):
            h = fit(m, key)
            if h:
                hits.append(f'{key[0]},{key[1]} unit={key[2]} sep={key[3]}: {h}')
        return m, hits

    from concurrent.futures import ThreadPoolExecutor
    ms = [l.split()[0] for l in src.read_text().splitlines() if '_' in l]
    with open(out_path, 'w', newline='\n') as out, ThreadPoolExecutor(max_workers=2) as pool:
        for m, hits in pool.map(scan, ms):
            out.write(f"{m}\t{len(hits)}\t{' || '.join(hits)}\n")
            out.flush()
            if hits:
                print('DIGIT-LIST (general)', m, hits[0][:150], flush=True)
    print('done', flush=True)


if __name__ == '__main__':
    main()
