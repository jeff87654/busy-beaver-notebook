"""Event-level simulator for the c35m14 exception machine (thread 2).
  python c35ev.py "TOKENS" [--r 6] [--steps 400] [--q G] [--machine M]
State: the D-token list left of the a-token (the a-token is exhausted, D(1)), accumulator r, tail D(4); head on the
blank right of the word in canonical state G.  One iteration:
  1. event: a literal run (evt.exe) from  TOKENS D(1) D(r) D(4)  until the first champion-phase lock that is followed by
     at least 2 verified R1/R2/R3 transitions (or stays locked); the list part of that K-moment is the post-event list;
  2. jump: the champion process clears the list from the right: tokens = 1 mod 3 (>= 4) -> D(1) (continue),
     = 2 mod 3 (>= 5) -> D(2) (stop), = 0 mod 3 (>= 6) -> D(3) (stop), D(0)/D(2)/D(3) stop.
Accumulators are always replaced by the small value r (default 6 = the real residue of R mod 12 in e=0 form), so new
big tokens D(2r+c) are small with the real residue mod 24 (this is the follower's loop acceleration, done at birth).
Prints every event; stops at a halt, a timeout, or STEPS iterations."""
import argparse
import os
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
JSTOP = os.environ.get('JSTOP', '3')
M2 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0LD0RH_1RG1LF_0LJ1RI_---0LA'


def toks(s):
    out = []
    for t in s.split():
        if t.startswith('<'):
            out.append(t)
            continue
        m = re.fullmatch(r'(\d+)(?:\*(\d+))?', t)
        if not m:
            raise ValueError(f'bad token {t!r}')
        out += [int(m.group(1))] * int(m.group(2) or 1)
    return out


def fmt(ts):
    out, i = [], 0
    while i < len(ts):
        j = i
        while j < len(ts) and ts[j] == ts[i]:
            j += 1
        out.append(str(ts[i]) + (f'*{j - i}' if j - i > 1 and not isinstance(ts[i], str) else ''))
        i = j
    return ' '.join(out)


def word(ts):
    import sys as _s
    _s.path.insert(0, str(HERE.parent / 'bb10_bb7_descendants'))
    import follow2 as _F
    out = ''
    for m in ts:
        out += _F.word_of(_F.parse_items(m)) if isinstance(m, str) else '10' * m + '1'
    return out


def event(machine, ts, r, q, maxsteps):
    w = word(ts + [1, r, 4])
    fd, path = tempfile.mkstemp(suffix='.txt')
    with os.fdopen(fd, 'w') as f:
        f.write(w)
    try:
        if os.environ.get('USEHYB'):
            out = subprocess.run([str(HERE.parent / 'bb10_bb7_descendants' / 'hyb10r.exe'), machine, path, str(len(w)), q, str(maxsteps),
                                  '-q', q, '-v', os.environ.get('USEHYB')], capture_output=True, text=True, creationflags=LOW).stdout.splitlines()
            last = out[-1] if out else ''
            if last.startswith('J '):
                h, b = last.split(' | ', 1)
                tl = re.search(r'tail=(\d+)', h).group(1)
                return 'J', f'J {h.split()[1]} tail={tl} | {b}', None
            return ('H' if last.startswith('H ') else 'T'), last, None
        out = subprocess.run([str(HERE / os.environ.get('EVTEXE', 'evt.exe')), machine, path, str(len(w)), q, str(maxsteps), '-q', q, '-r', '9', '-j', JSTOP,
                              '-m', '2000'], capture_output=True, text=True, creationflags=LOW).stdout.splitlines()
    finally:
        os.unlink(path)
    cand = None
    for line in out:
        if line.startswith('H '):
            return 'H', line, None
        if line.startswith('J '):
            return 'J', line, None
        if line.startswith('L '):
            cand = line
        elif line.startswith('U ') and cand is not None:
            c = [int(x) for x in line.split('|')[0].split()[2:5]]
            if sum(c) >= 2:
                return 'J', cand, None
            cand = None
    if cand is not None:
        return 'J', cand, None
    return 'T', out[-1] if out else '', None


def lock_list(line):
    head, body = line.split(' | ', 1)
    tl = int(re.search(r'tail=(\d+)', head).group(1))
    items = []
    for t in body.split():
        items += toks(t)
    return items[:len(items) - tl - 2]


def clear(ts):
    ts = list(ts)
    i = len(ts) - 1
    while i >= 0:
        m = ts[i]
        if isinstance(m, str):
            break
        if m == 1:
            i -= 1
            continue
        if m % 3 == 1 and m >= 4:
            ts[i] = 1
            i -= 1
            continue
        if m % 3 == 2 and m >= 5:
            ts[i] = 2
        elif m % 3 == 0 and m >= 6:
            ts[i] = 3
        break
    return ts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tokens')
    ap.add_argument('--r', type=int, default=6)
    ap.add_argument('--steps', type=int, default=400)
    ap.add_argument('--q', default='G')
    ap.add_argument('--machine', default=M2)
    ap.add_argument('--maxsteps', type=int, default=200_000_000)
    a = ap.parse_args()
    ts = toks(a.tokens)
    for it in range(a.steps):
        kind, line, _ = event(a.machine, ts, a.r, a.q, a.maxsteps)
        if kind != 'J':
            print(f'{it} {kind}: {line[:300]}', flush=True)
            return
        post = lock_list(line)
        ts = clear(post)
        print(f'{it} event -> {fmt(post)}   | cleared -> {fmt(ts)}', flush=True)


if __name__ == '__main__':
    main()
