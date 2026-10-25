"""Screen NOBOUNDARY digit-list rows for halting cases the graders do not probe.

dlscan2 grades the list-exhausted case R4 only on the empty list K(; 0; b) for b = 1..5 (dlscan.py similarly),
but a real run ends on an all-zero list K(0^n; 0; b) with n large, and the finale can loop over those zero
digits.  A machine that halts only for some (n, b) outside the probes - the BB(9) champion's pattern - would be
graded NOBOUNDARY and never dispatched.  This script runs R4 on the grid n = 0..6, b = 0..8 (r4grid.py), and for
any halting cell traces the machine from the blank tape to see whether the run reaches it.

  python nob_screen.py [--trace STEPS] [--rescreen]

Sources: neighbors/dl2_hits.tsv (grade or check_grade NOBOUNDARY; template from the row), neighbors/dl_hits.tsv
(DIGIT-LIST rows graded NOBOUNDARY; template from a dlscan2 refit) and the subtree watchers' watch_hits.tsv
(NOBOUNDARY rows) under investigations/champ12_subtree/ and investigations/bb9_from_bb8/ (9-state runs).  Results accumulate in neighbors/nob_screen.tsv; a machine is screened once.
Verdicts: CLEAN (no halting cell), GRID-HALT (some cell halts; `reached` says whether the blank-tape trace hit a
halting cell), NO-TEMPLATE (no dlscan2 fit to screen with).  Runs at Idle priority.  Prints one summary line,
and one line per new GRID-HALT row.
"""
from __future__ import annotations

import ctypes
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'investigations' / 'rebuilder_nbrs'))
from r4grid import grid, tmpl_from, mirror  # noqa: E402
from usage_phases import parse_tm  # noqa: E402

OUT = HERE / 'nob_screen.tsv'
EXE = HERE / 'dlscan2.exe'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
HEAD = 'machine\tsource\ttemplate\tverdict\treached\tgrid\tnote\ttime\n'


def set_idle():
    if sys.platform == 'win32':
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)


def rows(path):
    lines = path.read_text(encoding='utf-8').splitlines() if path.exists() else []
    if not lines:
        return []
    head = lines[0].split('\t')
    return [dict(zip(head, l.split('\t'))) for l in lines[1:] if l and not l.startswith('#')]


def sources():
    """(machine, source, template or None) for every NOBOUNDARY row."""
    out = []
    for r in rows(HERE / 'dl2_hits.tsv'):
        if 'NOBOUNDARY' in (r.get('grade'), r.get('check_grade')):
            out.append((r['machine'], f"dl2:{r.get('job', '?')}", r.get('template')))
    for r in rows(HERE / 'dl_hits.tsv'):
        if r.get('verdict') == 'DIGIT-LIST' and r.get('grade') == 'NOBOUNDARY':
            out.append((r['machine'], f"dl:{r.get('job', '?')}", None))
    watch = (sorted((ROOT / 'investigations' / 'champ12_subtree').glob('*/watch_hits.tsv'))
             + sorted((ROOT / 'investigations' / 'bb9_from_bb8').glob('*/watch_hits.tsv')))   # 9-state runs (2026-10-05)
    for w in watch:
        for line in w.read_text(encoding='utf-8').splitlines():
            f = line.split('\t')
            if len(f) >= 3 and f[0] == 'NOBOUNDARY':
                out.append((f[1], f'watch:{w.parent.name}', f[2]))
    return out


def refit(m):
    """Best dlscan2 template for a machine, or None."""
    with tempfile.TemporaryDirectory() as td:
        i, o = Path(td) / 'i.txt', Path(td) / 'o.tsv'
        i.write_text(m + '\n')
        try:
            subprocess.run([str(EXE), str(i), str(o)], creationflags=LOW, timeout=300,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return None
        rs = [l.split('\t') for l in o.read_text().splitlines()[1:] if not l.startswith('#')]
        return rs[0][4] if rs and rs[0][4] != '-' else None


def trace(m, tstr, halts, steps, wall=300):
    """Run from the blank tape; collect the all-zero-list family configurations (n, b) with a = 0."""
    o, T = tmpl_from(tstr)
    tm = parse_tm(mirror(m) if o == 'L' else m)
    tape, pos, q, hi = {}, 0, 0, -1
    seen, t0 = set(), time.time()
    for step in range(1, steps + 1):
        s = tape.get(pos, 0)
        tr = tm[(q, s)]
        if tr is None:
            return f'HALTS at step {step} from blank', True, seen
        w, d, q = tr
        if w:
            tape[pos] = 1
            if pos > hi:
                hi = pos
        elif s:
            del tape[pos]
            if pos == hi:
                hi = max(tape) if tape else -1
        pos += d
        if q == T.q and tape and hi < pos <= hi + 4:   # the word may end in up to 3 zeros
            x = ''.join('1' if tape.get(i, 0) else '0' for i in range(min(tape), pos))
            k = T.parse(x)
            if k is not None and k[1] == 0 and all(v == 0 for v in k[0]):
                seen.add((len(k[0]), k[2]))
                if (len(k[0]), k[2]) in halts:
                    return f'reaches halting cell n={len(k[0])} b={k[2]} at step {step}', True, seen
        if step % 100000 == 0 and time.time() - t0 > wall:
            return f'not reached in {step} steps (wall limit)', False, seen
    return f'not reached in {steps} steps', False, seen


def main():
    set_idle()
    steps = int(sys.argv[sys.argv.index('--trace') + 1]) if '--trace' in sys.argv else 5_000_000
    done = {l.split('\t')[0] for l in OUT.read_text(encoding='utf-8').splitlines()[1:]} if OUT.exists() else set()
    if '--rescreen' in sys.argv or not OUT.exists():
        OUT.write_text(HEAD, encoding='utf-8')
        done = set()
    todo, seen_m = [], set(done)
    for m, src, t in sources():
        if m not in seen_m:
            seen_m.add(m)
            todo.append((m, src, t))
    new_hits = []
    with OUT.open('a', encoding='utf-8') as f:
        for m, src, t in todo:
            note, reached, gridstr = '', '-', '-'
            if not t or t == '-':
                t = refit(m)
            if not t or tmpl_from(t)[1] is None:
                verdict = 'NO-TEMPLATE'
            else:
                lines, letters = grid(m, t, 6, 8, 200_000)
                gridstr = ' '.join(f'n{n}:{s}' for n, s in enumerate(lines))
                halts = {(n, b) for n, s in enumerate(lines) for b, c in enumerate(s) if c == 'H'}
                if not halts:
                    verdict = 'CLEAN'
                else:
                    verdict = 'GRID-HALT'
                    note, hit, seen = trace(m, t, halts, steps)
                    reached = 'REACHED' if hit else 'unreached'
                    if not hit and seen:
                        note += '; all-zero states seen (n,b): ' + ' '.join(f'({n},{b})' for n, b in sorted(seen)[:12])
                    new_hits.append(f'NOB-SCREEN GRID-HALT [{reached}] {src} {m}: {note}')
            f.write('\t'.join([m, src, t or '-', verdict, reached, gridstr, note,
                               time.strftime('%Y-%m-%d_%H:%M')]) + '\n')
            f.flush()
    allrows = rows(OUT)
    tally = {}
    for r in allrows:
        tally[r['verdict']] = tally.get(r['verdict'], 0) + 1
    for h in new_hits:
        print(h)
    print(f'nob-screen: {len(allrows)} NOBOUNDARY machines screened ({len(todo)} new this run); '
          f'{", ".join(f"{k} {v}" for k, v in sorted(tally.items()))}')


if __name__ == '__main__':
    main()
