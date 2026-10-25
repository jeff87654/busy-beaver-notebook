"""Dispatch order for bb8-investigator subagents (the 6-hourly check-in launches the top row).

  python dispatch_queue.py          # the whole queue
  python dispatch_queue.py --top    # only the first row (or "queue empty")

Policy (user decision 2026-10-04: "I'd hate to miss a record machine by accident"; tokens are not a constraint):
  0 RECORD     a CHAMPION-structure machine whose first list is longer than 35 digits (subtree watchers;
               would beat 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_1LC0RH_1RG1LF)
  1 CHAMPION   new dl2_hits rows with check_grade CHAMPION (the BB(7) champion's structure)
  2 R4-SOME    new dl2_hits rows / watcher rows: the list-exhausted case halts for some b only (BB(9) pattern)
  3 GRID-HALT  nob_screen.py rows whose (n, b) grid halts somewhere (REACHED before unreached)
  4 HALT?/HALT-SOME/CHECK  new dl_hits DIGIT-LIST rows, new dl2_hits rows, watcher rows
  5 NOBOUNDARY new dl_hits / dl2_hits rows and watcher rows (screened CLEAN or unscreenable) whose R1 grows b.
PROOF BACKLOG (never dispatched; user decision 2026-10-08): NOBOUNDARY rows whose R1 has a constant slope
  (`R1 0b+c`). They are plain counters, not Ackermann-type, so even a halting one cannot be record class; 16 earlier
  NOBOUNDARY dispatches found no halter at ~400k tokens each. They only matter for list completeness: try the
  automatic n-gram prover (investigations/bb8_m7_0RB0LC_ctl/ngcps_queue.py) on them, nothing more.
  `python dispatch_queue.py --backlog` lists them.
Excluded: machines that are not 8-state (e.g. the 9-state c7m12 rows that nob_screen also screens; those are triaged
in investigations/bb9_from_bb8 with bign_probe.py and dedicated investigations, 2026-10-06; they are only counted),
machines listed in ../investigations/dispatched.txt (first column), dl/dl2 rows marked `known`,
watcher CHAMPION rows with a start of at most 35 digits (known start-ups that halt below the record), and the
doubling queue (never dispatched).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RECORD_DIGITS = 35
MID = ('HALT?', 'HALT-SOME', 'CHECK')


def rows(path):
    lines = path.read_text(encoding='utf-8').splitlines() if path.exists() else []
    if not lines:
        return []
    head = lines[0].split('\t')
    return [dict(zip(head, l.split('\t'))) for l in lines[1:] if l and not l.startswith('#')]


def const_slope(text):
    """True if the best fit's R1 does not grow b (`R1 0b+c` in dlscan2 params, `R1: b -> 0b+c` in dlscan details)."""
    m = re.search(r'R1:? (?:b -> )?(\d+)b', text or '')
    return bool(m) and m.group(1) == '0'


def start_digits(s):
    m = re.search(r'K\(([^;]*);', s or '')
    if not m:
        return None
    return len([x for x in m.group(1).split(',') if x.strip()])


def main():
    disp = set()
    dpath = ROOT / 'investigations' / 'dispatched.txt'
    if dpath.exists():
        disp = {l.split('\t')[0].strip() for l in dpath.read_text(encoding='utf-8').splitlines() if l.strip()}
    q = []   # (priority, sub-order, source, machine, detail)
    for w in sorted((ROOT / 'investigations' / 'champ12_subtree').glob('*/watch_hits.tsv')):
        for line in w.read_text(encoding='utf-8').splitlines():
            f = line.split('\t')
            if len(f) < 3:
                continue
            g, m, src = f[0], f[1], f'watch:{w.parent.name}'
            start = f[4] if len(f) > 4 else ''
            if g == 'CHAMPION':
                nd = start_digits(start)
                if nd is not None and nd > RECORD_DIGITS:
                    q.append((0, -nd, src, m, f'CHAMPION start {nd} digits ({start[:40]})'))
            elif g == 'R4-SOME':
                q.append((2, 0, src, m, 'R4-SOME'))
            elif g in MID:
                q.append((4, 0, src, m, g))
            elif g == 'NOBOUNDARY':
                c = const_slope(f[3] if len(f) > 3 else '')
                q.append((5, int(c), src, m, 'NOBOUNDARY' + (' (constant-slope R1)' if c else '')))
    for r in rows(HERE / 'dl2_hits.tsv'):
        if r.get('known') != 'new':
            continue
        g, src = r.get('check_grade'), f"dl2:{r.get('job')}"
        if g == 'CHAMPION':
            q.append((1, 0, src, r['machine'], 'CHAMPION'))
        elif g == 'R4-SOME':
            q.append((2, 0, src, r['machine'], 'R4-SOME'))
        elif g in MID:
            q.append((4, 0, src, r['machine'], g))
        elif g == 'NOBOUNDARY':
            c = const_slope(r.get('params'))
            q.append((5, int(c), src, r['machine'], 'NOBOUNDARY' + (' (constant-slope R1)' if c else '')))
    for r in rows(HERE / 'dl_hits.tsv'):
        if r.get('known') != 'new' or r.get('verdict') != 'DIGIT-LIST':
            continue
        g, src = r.get('grade'), f"dl:{r.get('job')}"
        if g in ('R4-SOME',):
            q.append((2, 0, src, r['machine'], g))
        elif g in MID:
            q.append((4, 0, src, r['machine'], g))
        elif g == 'NOBOUNDARY':
            c = const_slope(r.get('details'))
            q.append((5, int(c), src, r['machine'], 'NOBOUNDARY' + (' (constant-slope R1)' if c else '')))
    for r in rows(HERE / 'nob_screen.tsv'):
        if r.get('verdict') == 'GRID-HALT':
            q.append((3, 0 if r.get('reached') == 'REACHED' else 1, f"nob:{r.get('source')}", r['machine'],
                      f"GRID-HALT {r.get('reached')}: {r.get('note', '')[:80]}"))
    best, other_states = {}, set()
    for item in sorted(q):
        if len(item[3]) != 55:              # not an 8-state machine string (7*8 - 1 characters)
            if item[3] not in disp:
                other_states.add(item[3])
            continue
        if item[3] in disp or item[3] in best:
            continue
        best[item[3]] = item
    backlog = sorted(v for v in best.values() if v[0] == 5 and v[1] == 1)
    queue = sorted(v for v in best.values() if not (v[0] == 5 and v[1] == 1))
    if '--backlog' in sys.argv:
        for src, m in sorted((v[2], v[3]) for v in backlog):
            print(f'{src:<14} {m}')
        print(f'{len(backlog)} constant-slope NOBOUNDARY machines on the proof backlog (not dispatched)')
        return
    names = {0: 'RECORD', 1: 'CHAMPION', 2: 'R4-SOME', 3: 'GRID-HALT', 4: 'MID', 5: 'NOBOUNDARY'}
    if '--top' in sys.argv:
        if not queue:
            print('queue empty')
        else:
            p, _, src, m, det = queue[0]
            print(f'TOP {names[p]} {src} {m}  {det}  ({len(queue)} in queue)')
        return
    for i, (p, _, src, m, det) in enumerate(queue, 1):
        print(f'{i:>3} {names[p]:<10} {src:<14} {m}  {det}')
    print(f'{len(queue)} machines in the dispatch queue'
          + f'; {len(backlog)} constant-slope rows on the proof backlog (--backlog)'
          + (f' ({len(other_states)} non-8-state rows not dispatched; see investigations/bb9_from_bb8)' if other_states else ''))


if __name__ == '__main__':
    main()
