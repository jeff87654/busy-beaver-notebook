"""Free-slot roots: keep a digit-list machine's counting transitions, free the rarely used ones (resets, rebuilds,
start-up, halts), so `knuth8.exe exactsplit ROOT 8 2 C ...` enumerates every completion of the free slots with the
enumerator's deciders.

  python freeslots.py machines.txt > roots.tsv      (one machine per line; '#' lines ignored)

A transition is free if it is undefined, or in a 2*10^8-step literal run from the blank tape it fires in at most
50 episodes (episodes = bursts separated by > 1000 steps) or in under 10^-6 of the steps. A0 is never freed. Roots with
fewer than 2 or more than MAXFREE free slots are skipped.
A parent with fewer than 8 states gets fully free extra states (counted in the free slots). Output: root, number of free slots, free slot names, source machines.
"""
import subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
STEPS, MAXFREE = 200_000_000, 9

def free_of(tm):
    out = subprocess.run([str(HERE / 'usage.exe'), tm, str(STEPS)], capture_output=True, text=True).stdout
    total = None; rows = []
    for line in out.splitlines():
        if line.startswith('halt at'):
            total = int(line.split()[2])
        if line[:1].isalpha() and 'count=' in line:
            f = dict(kv.split('=') for kv in line.split()[2:])
            rows.append((line.split()[0], line.split()[1], int(f['count']), int(f['episodes'])))
    steps = total or STEPS
    return [name for name, tr, cnt, ep in rows if name != 'A0' and (tr == '---' or ep <= 50 or cnt < 1e-6 * steps)], total

def root_of(tm, free):
    rows = tm.split('_')
    for name in free:
        q, c = ord(name[0]) - 65, int(name[1])
        rows[q] = rows[q][:3 * c] + '---' + rows[q][3 * c + 3:]
    return '_'.join(rows)

roots = {}
for line in open(sys.argv[1]):
    tm = line.split()[0] if line.strip() and not line.startswith('#') else None
    if not tm:
        continue
    free, halted = free_of(tm)
    if halted is not None:
        print(f"# {tm} halts at {halted}, skipped", file=sys.stderr); continue
    r = root_of(tm, free)
    while r.count('_') < 7:          # 7-state parent: add a fully free 8th state
        r += '_------'; free = free + [f'{chr(65 + r.count("_"))}0', f'{chr(65 + r.count("_"))}1']
    if len(free) < 2:
        print(f"# {tm} has only {free} free, skipped", file=sys.stderr); continue
    if len(free) > MAXFREE:
        print(f"# {tm} has {len(free)} free slots {free}, skipped", file=sys.stderr); continue
    roots.setdefault(r, [len(free), ','.join(free), []])[2].append(tm)
for r, (n, f, src) in roots.items():
    print(f"{r}\t{n}\t{f}\t{' '.join(src)}")
