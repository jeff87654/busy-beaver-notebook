"""Mini event follower in g's merged-counter world, several proxy accumulators per event.
  python fol9b.py MACHINE "TOKENS" X1,X2,.. [--events N] [--steps S] [--thr T]
As fol9.py, but every event is run for each X (accumulator D(X), X = 3b+2) from the same token configuration:
  - a HALT for any X is reported (with the tape) and stops the follower;
  - the token count at the next hit is compared across X: a difference means the next list's length depends on the
    accumulator ('ACCDEP', i.e. a rebuild of accumulator length); 'zeros=' = tokens cleared by the jump;
  - the follower continues from the first X's hit.
Snapshots must end in g's tail form `0*6 <1 00> (0*5 <1 00>)^u 0*5 <1 00 1 00> 0`; u is logged."""
import argparse, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from nxt import build, abbr, TAIL, tok2word, LOW
from jump import expand

TAILRX = re.compile(r'^(.*?) 0\*6 <1 00> ((?:0\*5 <1 00> )*)0\*5 <1 00 1 00> 0$')
if not TAILRX.match('x 1 ' + TAIL):
    raise SystemExit('tail regex does not match g tail')


def canon(line):
    body = line.split(' | ', 1)[1].strip()
    mm = TAILRX.match(body)
    if not mm:
        return None, None
    head = mm.group(1).strip()
    v = re.findall(r'<[^>]*>|\S+', head)
    if len(v) < 2 or not re.fullmatch(r'\d+', v[-1]) or not re.fullmatch(r'\d+', v[-2]):
        return None, None
    return head, mm.group(2).count('<')


SHRINK = 0


def jumpcfg(head):
    v = expand(head)[:-1]
    for i in range(len(v) - 1, -1, -1):
        t = v[i]
        if t.startswith('<') or int(t) % 3 != 1:
            j = i; break
    else:
        raise SystemExit('no blocker in ' + head)
    if SHRINK and v[j].isdigit() and int(v[j]) > SHRINK:   # big non-3d+1 blocker: keep its class mod 12
        v[j] = str(int(v[j]) % 12 + 12)
    cleared = len(v) - 1 - j
    return ' '.join(v[:j + 1] + ['1'] * cleared), v[j], cleared, j + 1


def run_event(M, cfg, X, steps, thr):
    w = tok2word(build(cfg, X))
    p = subprocess.Popen([str(HERE / 'tr9t.exe'), M, w, str(len(w)), 'B', str(steps), 'dall', '1000000000'],
                         stdout=subprocess.PIPE, text=True, creationflags=LOW)
    nsnap = 0; last = None
    try:
        for line in p.stdout:
            if line.startswith('S '):
                nsnap += 1
                c, u = canon(line)
                if c is None:
                    if not re.search(r'0\*5 <1 00 1 00> 0\s*$', line):
                        last = ('TAILCHANGE', abbr(line)[:300])
                    continue
                v = expand(c)
                nums = [int(t) for t in v if t.isdigit()]
                if nsnap > 1 and max(nums[-6:]) > thr:
                    return ('HIT', c, u, int(line.split()[1]))
            elif line.startswith('HALT') or line.startswith('END'):
                return (line.split()[0], line.strip(), abbr(p.stdout.readline().strip())[:500], last)
        return ('EOF', last)
    finally:
        p.kill()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('machine'); ap.add_argument('tokens'); ap.add_argument('xs')
    ap.add_argument('--events', type=int, default=60); ap.add_argument('--steps', type=int, default=100_000_000)
    ap.add_argument('--thr', type=int, default=30)
    ap.add_argument('--shrink', type=int, default=0, help='reduce a numeric blocker > SHRINK to its class mod 12 (+12)')
    a = ap.parse_args()
    SHRINK = a.shrink
    xs = [int(x) for x in a.xs.split(',')]
    cfg = a.tokens
    for ev in range(a.events):
        res = {X: run_event(a.machine, cfg, X, a.steps, a.thr) for X in xs}
        for X, r in res.items():
            if r[0] != 'HIT':
                print(f'EV{ev} X={X} {r[0]}: ' + ' | '.join(str(x) for x in r[1:]), flush=True)
        if any(r[0] == 'HALT' for r in res.values()) or res[xs[0]][0] != 'HIT':
            sys.exit(0)
        hits = {X: r for X, r in res.items() if r[0] == 'HIT'}
        counts = {X: len(expand(r[1])) for X, r in hits.items()}
        shapes = {X: re.sub(r'\d+', '#', r[1]) for X, r in hits.items()}
        dep = 'ACCDEP' if len(set(counts.values())) > 1 else ('shape-diff' if len(set(shapes.values())) > 1 else '')
        h = hits[xs[0]]
        cfg, blk, cleared, ntok = jumpcfg(h[1])
        print(f'EV{ev} @{h[3]} u={h[2]} counts={list(counts.values())} {dep} hit: {abbr(h[1])[:170]}\n'
              f'    -> blocker {blk}->{cfg.split()[-1 - cleared]} zeros={cleared} tokens={ntok}', flush=True)
