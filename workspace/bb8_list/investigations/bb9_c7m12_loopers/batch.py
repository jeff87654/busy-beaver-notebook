"""batch.py: blank-tape emulation check + fol2 mini-follower (with slope probes) for the rows of rows.tsv.
  python batch.py ROWS.tsv PART NPARTS --b0 6 [--stages 24] [--maxs 3e7]
Writes res_b{b0}_{PART}.tsv (append; machines already present are skipped) and logs/<machine>_b{b0}.log.
Columns: machine, grade, undefined, emu (step of K(1^11;1;2) from blank or NO), result, nstages, halt slot@stage,
undefined slots read, cleared-list sequence, slopes (token change per r+42 at fresh-accumulator stages), far bits seq."""
import sys, argparse, threading, ctypes, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)   # IDLE
except Exception:
    pass
import fol2, mf35
from emu_check import check
ap = argparse.ArgumentParser()
ap.add_argument('rows'); ap.add_argument('part', type=int); ap.add_argument('nparts', type=int)
ap.add_argument('--b0', type=int, default=6); ap.add_argument('--stages', type=int, default=24)
ap.add_argument('--maxs', type=float, default=3e7)
a = ap.parse_args()
rows = [l.rstrip('\n').split('\t') for l in open(a.rows) if l.strip()]
rows = rows[a.part::a.nparts]
out = HERE / f'res_b{a.b0}_{a.part}.tsv'
done = set(l.split('\t')[0] for l in out.read_text().splitlines()) if out.exists() else set()
(HERE / 'logs').mkdir(exist_ok=True)
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)


def one(r):
    m, g, und = r[0], r[1], r[2]
    emu = check(m)
    lf = open(HERE / 'logs' / f'{m}_b{a.b0}.log', 'w')

    def log(x):
        lf.write(x + '\n'); lf.flush()
    log(f'# {m} grade={g} undefined={und} emu={emu} b0={a.b0}')
    toks = [0, 0] + [1] * 12 + [3 * a.b0 + 2]
    w = mf35.word_of_tokens(toks) + fol2.SUF
    try:
        hist, used = fol2.follow(m, w, len(w), fol2.Q, a.stages, a.maxs, True, log)
    except Exception as ex:
        log(f'CRASH {ex!r}')
        return [m, g, und, str(emu), 'CRASH', '0', '-', '-', '-', '-', '-']
    last = hist[-1] if hist else {'kind': 'NONE'}
    hs = f"{last['slot']}@{last['s']}" if last['kind'] == 'H' else '-'
    zs = ' '.join(str(h.get('zeros', '')) for h in hist if h['kind'] == 'J')
    sl = ' '.join(f"{h['s']}:{h['slope'][0]:+d}" for h in hist if 'slope' in h)
    far = ' '.join(str(h.get('far', '')) for h in hist if h['kind'] == 'J')
    uu = ','.join(x for x in fol2.undef_slots(m) if x in used) or '-'
    log(f'RESULT {last["kind"]} stages={len(hist)} halt={hs} undefined_read={uu}')
    with open(HERE / 'logs' / f'{m}_b{a.b0}.json', 'w') as jf:
        json.dump({'machine': m, 'b0': a.b0, 'hist': [{k: v for k, v in h.items() if k != 'next_alt'} for h in hist],
                   'used': used}, jf)
    return [m, g, und, str(emu), last['kind'], str(len(hist)), hs, uu, zs, sl, far]


def main():
    for r in rows:
        if r[0] in done:
            continue
        res = one(r)
        with out.open('a') as f:
            f.write('\t'.join(res) + '\n')
        print('\t'.join(res[:8]), flush=True)


t = threading.Thread(target=main); t.start(); t.join()
