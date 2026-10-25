"""Mini event follower in g's merged-counter world (proxy accumulators).
  python fol9.py MACHINE "TOKENS" X [--events N] [--steps S] [--thr T]
Start: TOKENS (Pn macro as in nxt.py) + accumulator D(X) + g's real tail, head in B on the right edge.
Loop: literal run (tr9 dall) until a canonical snapshot (numeric a-digit and accumulator token followed by g's tail)
has a token > THR (or the accumulator > THR); then JUMP: the rightmost token that is not a 3d+1 digit (residue != 1
mod 3, or raw) is the blocker; it is kept unchanged; every token right of it is set to D1 (= 0) and the
accumulator to D(X). Logs per event: blocker, number of cleared tokens ('zeros='), total token count, the token list.
Halts / tail changes / non-canonical endings are reported and stop the follower (nothing is guessed)."""
import argparse, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from nxt import build, abbr, TAIL, tok2word, LOW
from jump import expand

ap = argparse.ArgumentParser()
ap.add_argument('machine'); ap.add_argument('tokens'); ap.add_argument('X', type=int)
ap.add_argument('--events', type=int, default=12); ap.add_argument('--steps', type=int, default=200_000_000)
ap.add_argument('--thr', type=int, default=30)
a = ap.parse_args()
TAILRX = re.compile(r'^(.*?) 0\*6 <1 00> ((?:0\*5 <1 00> )*)0\*5 <1 00 1 00> 0$')
if not TAILRX.match('x 1 ' + TAIL):
    raise SystemExit('tail regex does not match g tail')


def canon(line):
    """return token list (with a-digit and acc as the last two) of a canonical snapshot, or None"""
    body = line.split(' | ', 1)[1].strip()
    mm = TAILRX.match(body)
    if not mm:
        return None
    head = mm.group(1).strip()
    canon.units = mm.group(2).count('<')
    v = re.findall(r'<[^>]*>|\S+', head)
    if len(v) < 2 or not re.fullmatch(r'\d+', v[-1]) or not re.fullmatch(r'\d+', v[-2]):
        return None
    return head


def jumpcfg(head):
    v = expand(head)[:-1]          # drop the accumulator
    for i in range(len(v) - 1, -1, -1):
        t = v[i]
        if t.startswith('<') or int(t) % 3 != 1:
            j = i; break
    else:
        raise SystemExit('no blocker in ' + head)
    cleared = len(v) - 1 - j
    return ' '.join(v[:j + 1] + ['1'] * cleared), v[j], cleared, j + 1


cfg = a.tokens
for ev in range(a.events):
    full = build(cfg, a.X)
    w = tok2word(full)
    p = subprocess.Popen([str(HERE / 'tr9t.exe'), a.machine, w, str(len(w)), 'B', str(a.steps), 'dall', '100000000'],
                         stdout=subprocess.PIPE, text=True, creationflags=LOW)
    hit = None; last = None; nsnap = 0
    for line in p.stdout:
        if line.startswith('S '):
            nsnap += 1
            c = canon(line)
            if c is None:
                # tail must still be g's tail
                if not re.search(r'0\*5 <1 00 1 00> 0\s*$', line):
                    last = 'TAILCHANGE ' + abbr(line)[:300]
                continue
            v = expand(c)
            nums = [int(t) for t in v if t.isdigit()]
            last = c
            if nsnap > 1 and (int(v[-1]) > a.thr or max(nums[-6:]) > a.thr):
                hit = c; break
        elif line.startswith('HALT') or line.startswith('END'):
            last = line.strip()
            nxtl = p.stdout.readline()
            print(f'EV{ev} {line.strip()} | {abbr(nxtl.strip())[:400]}')
            p.wait(); sys.exit(0)
    p.kill()
    if hit is None:
        print(f'EV{ev} NO-CANONICAL-HIT last={abbr(str(last))[:300]}'); sys.exit(0)
    cfg, blk, cleared, ntok = jumpcfg(hit)
    print(f'EV{ev} hit: {abbr(hit)[:200]}\n    -> blocker {blk} zeros={cleared} tokens={ntok} | {abbr(cfg)[-160:]}', flush=True)
