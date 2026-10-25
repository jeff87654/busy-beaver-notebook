"""screen.py: fol2 mini-follower screen of clone-split completions.
  python screen.py MACHINES.txt PART NPARTS [--b0s 6,20] [--stages 10] [--maxs 3e7]
Writes scr_PART.tsv (append, resumable): machine, b0, result, nstages, halt slot@stage, cleared-list (zeros) sequence,
K token counts.  Logs to slogs/<machine>_b<b0>.log."""
import sys, argparse, threading, ctypes, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb9_c7m12_loopers')
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:
    pass
import fol2, mf35
ap = argparse.ArgumentParser()
ap.add_argument('rows'); ap.add_argument('part', type=int); ap.add_argument('nparts', type=int)
ap.add_argument('--b0s', default='6,20'); ap.add_argument('--stages', type=int, default=10)
ap.add_argument('--maxs', type=float, default=3e7); ap.add_argument('--tag', default='scr')
a = ap.parse_args()
ms = [l.split()[0] for l in open(a.rows) if l.strip() and not l.startswith('#')][a.part::a.nparts]
out = HERE / f'{a.tag}_{a.part}.tsv'
done = set(tuple(l.split('\t')[:2]) for l in out.read_text().splitlines()) if out.exists() else set()
(HERE / 'slogs').mkdir(exist_ok=True)
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)


def one(m, b0):
    lf = open(HERE / 'slogs' / f'{m}_b{b0}.log', 'w')

    def log(x):
        lf.write(x + '\n'); lf.flush()
    log(f'# {m} b0={b0}')
    w = mf35.word_of_tokens([0, 0] + [1] * 12 + [3 * b0 + 2]) + fol2.SUF
    try:
        hist, used = fol2.follow(m, w, len(w), fol2.Q, a.stages, a.maxs, False, log)
    except Exception as ex:
        log(f'CRASH {ex!r}')
        return [m, str(b0), 'CRASH', '0', '-', '-', '-']
    last = hist[-1] if hist else {'kind': 'NONE'}
    hs = f"{last['slot']}@{last['s']}:{last['step']}" if last['kind'] == 'H' else '-'
    zs = ' '.join(str(h.get('zeros', '')) for h in hist if h['kind'] == 'J')
    nt = ' '.join(str(h.get('ntok', '')) for h in hist if h['kind'] == 'J')
    log(f'RESULT {last["kind"]} stages={len(hist)} halt={hs}')
    return [m, str(b0), last['kind'], str(len(hist)), hs, zs, nt]


def main():
    for m in ms:
        for b0 in a.b0s.split(','):
            if (m, b0) in done:
                continue
            res = []
            t = threading.Thread(target=lambda: res.append(one(m, int(b0))))
            t.start(); t.join()
            r = res[0] if res else [m, b0, 'CRASH', '0', '-', '-', '-']
            with open(out, 'a') as f:
                f.write('\t'.join(r) + '\n')


main()
