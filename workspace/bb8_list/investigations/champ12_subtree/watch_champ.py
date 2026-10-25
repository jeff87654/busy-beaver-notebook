"""Hourly interim grading of a running champion-subtree enumeration (e.g. m7/).

  python watch_champ.py DIR [BEST=35]

Each round: new holdouts (DIR/part_*.txt minus DIR/watched.txt) are graded with dlscan2 (Idle); every CHAMPION /
NOBOUNDARY / R4-SOME / HALT? / HALT-SOME row is traced from the blank tape with its own template (trace2.exe) and its
first family configuration recorded in DIR/watch_hits.tsv. Prints one line per round, and "RECORD-LENGTH ..." for a
CHAMPION machine whose first list is longer than BEST digits. Exits when all parts have finished (part_*.json with "root").
"""
import re, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
NB = HERE.parent.parent / 'neighbors'
D = HERE / sys.argv[1]; BEST = int(sys.argv[2]) if len(sys.argv) > 2 else 35
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
seen_f = D / 'watched.txt'; hits_f = D / 'watch_hits.tsv'
GR = ('CHAMPION', 'NOBOUNDARY', 'R4-SOME', 'HALT?', 'HALT-SOME', 'CHECK')

def first_cfg(m, t):
    o, q, rest = t.split(',', 2)
    kv = dict(x.split('=', 1) for x in rest.split(','))
    al, be = re.match(r'(\d+)d([+-]\d+)', kv['d']).groups(); alB, beB = re.match(r'(\d+)b([+-]\d+)', kv['b']).groups()
    out = subprocess.run([str(NB / 'trace2.exe'), m, o, q, kv['P'], kv['u'], kv['s'], al, be, alB, beB, kv['S'], '200000000', '1'],
                         capture_output=True, text=True, creationflags=LOW).stdout.strip()
    return out

while True:
    done = all('"root"' in p.read_text(errors='ignore') for p in D.glob('part_*.json')) and len(list(D.glob('part_*.json'))) > 0
    seen = set(seen_f.read_text().split()) if seen_f.exists() else set()
    cur = set()
    for p in D.glob('part_*.txt'):
        cur |= set(p.read_text(errors='ignore').split())
    # a machine string of n states has 7n - 1 characters (55 for 8 states, 62 for 9; fixed 2026-10-05)
    new = sorted(m for m in cur - seen if '_' in m and len(m) == 7 * (m.count('_') + 1) - 1)
    if new:
        (D / 'watch_new.txt').write_text('\n'.join(new) + '\n')
        subprocess.run([str(NB / 'dlscan2.exe'), str(D / 'watch_new.txt'), str(D / 'watch_new_dl2.tsv'), '1000000', '20000'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=LOW)
        grades = {}
        with open(hits_f, 'a') as hf:
            for line in open(D / 'watch_new_dl2.tsv'):
                f = line.rstrip('\n').split('\t')
                if len(f) < 6 or f[3] not in GR: continue
                grades[f[3]] = grades.get(f[3], 0) + 1
                cfg = first_cfg(f[0], f[4])
                hf.write('\t'.join([f[3], f[0], f[4], f[5], cfg]) + '\n')
                mm = re.search(r'K\(([\d,]*);', cfg)
                n = len(mm.group(1).split(',')) if mm and mm.group(1) else 0
                if f[3] == 'CHAMPION' and n > BEST:
                    print(f'RECORD-LENGTH {n} digits {f[0]} {cfg}', flush=True)
        with open(seen_f, 'a') as sf:
            sf.write('\n'.join(new) + '\n')
        print(time.strftime('%H:%M'), f'{len(new)} new holdouts graded, total {len(cur)}, grades {grades}', flush=True)
    if done:
        print('all parts finished', flush=True); break
    time.sleep(3600)
