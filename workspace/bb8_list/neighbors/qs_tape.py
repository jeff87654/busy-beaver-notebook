"""Nested-counter signal from Ligocki's Quick_Sim: the compressed tape after a fixed simulation time.

  python qs_tape.py OUT.tsv [--time 10] [--workers 2] [--queue | machines...]

`--queue` takes the undecided doubling-class queue (doubling rows of followup/promising.tsv that the pre-filter
did not decide and that were never dispatched). For each machine, Quick_Sim (unmodified, --recursive) runs for
--time CPU-seconds of simulation; then its compressed tape is read: a list of blocks symbol^n on each side of
the head. A digit-list machine keeps many counters at once, so its tape has many blocks with large exponents
(the BB(7) champion: one block (01)^(3d+1) per digit); a plain exponential or doubling counter has a few.
Columns: machine, status, large counters (non-blank blocks with exponent >= 1000), big blocks (exponent >= 3),
non-blank blocks, and the tape (exponents of more than 12 digits are shown as ~10^d).
Calibration at 10 s: the BB(7) champion and the digit-list machine of subtask 240161 have 3 large counters; the
1RB1RA Ackermann parent (whose list is still one digit long) and three proved doubling-class non-halters have 2.
"""
import contextlib
import io
import json
import multiprocessing as mp
import runpy
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROJECT = ROOT.parent
CODE = PROJECT / 'third_party' / 'ligocki' / 'Code'
DEPS = PROJECT / 'third_party' / 'python_deps'


def digits_of(num):
    try:
        v = int(num)
        return len(str(abs(v))), v
    except Exception:
        s = str(num)
        return 10 ** 6, None   # symbolic or approximate: treat as huge


def child(machine, sim_time, q):
    sys.path[:0] = [str(CODE), str(DEPS)]
    sys.argv = [str(CODE / 'Quick_Sim.py'), '--quiet', '--recursive', '--max-loops', '100000000', machine]
    out = {'machine': machine}
    try:
        from Macro import Simulator as _Sim, Turing_Machine as _TM
        clock = {}
        orig = _Sim.Simulator.step

        def timed(self):
            now = time.monotonic()
            clock.setdefault('deadline', now + sim_time)
            if self.op_state == _TM.RUNNING and now > clock['deadline']:
                self.op_state = _TM.TIME_OUT
                return
            return orig(self)
        _Sim.Simulator.step = timed
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            sim = runpy.run_path(str(CODE / 'Quick_Sim.py'), run_name='__main__')['sim']
        names = {_TM.HALT: 'halt', _TM.INF_REPEAT: 'infinite', _TM.TIME_OUT: 'cutoff', _TM.RUNNING: 'cutoff'}
        out['status'] = names.get(sim.op_state, 'other')
        blocks = []
        for side in (0, 1):
            for b in sim.tape.tape[side]:
                d, v = digits_of(b.num)
                blocks.append((side, str(b.symbol), d, v))
        out['blocks'] = blocks
    except BaseException as e:
        out['status'] = 'error: %s' % type(e).__name__
        out['blocks'] = []
    q.put(out)


def run(machine, sim_time):
    q = mp.Queue()
    p = mp.Process(target=child, args=(machine, sim_time, q))
    p.start()
    try:
        res = q.get(timeout=sim_time * 4 + 120)
    except Exception:
        res = {'machine': machine, 'status': 'timeout', 'blocks': []}
    p.join(5)
    if p.is_alive():
        p.kill()
    return res


def queue():
    pf = json.loads((ROOT / 'prefilter_results.json').read_text())
    decided = {m for m, r in pf.items() if r['status'] == 'verified_nonhalting'}
    disp = ROOT / 'investigations' / 'dispatched.txt'
    dispatched = {l.split('\t')[0] for l in disp.read_text().splitlines() if l.strip()}
    rows = (ROOT / 'followup' / 'promising.tsv').read_text().splitlines()[1:]
    ms = [l.split('\t')[-1].strip() for l in rows if l.startswith('doubling\t')]
    return [m for m in dict.fromkeys(ms) if m not in decided and m not in dispatched]


def fmt(res):
    blocks = [x for x in res['blocks'] if '1' in x[1]]          # the blank padding is not a counter
    big = [x for x in blocks if x[3] is None or x[3] >= 3]
    large = [x for x in blocks if x[3] is None or x[3] >= 1000]
    tape = ' '.join(('%s^%s' % (s, v if v is not None and d <= 12 else '~10^%d' % d)) if (v is None or v > 1) else s
                    for side, s, d, v in res['blocks'])
    return [res['machine'], res['status'], str(len(large)), str(len(big)), str(len(blocks)), tape[:600]]


def main():
    args = [a for a in sys.argv[1:]]
    opt = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
    sim_time, workers = opt('--time', 10.0), opt('--workers', 2)
    out = Path(args[0])
    ms = queue() if '--queue' in args else [a for a in args[1:] if '_' in a]
    from concurrent.futures import ThreadPoolExecutor
    with open(out, 'w', newline='\n') as f, ThreadPoolExecutor(workers) as pool:
        f.write('machine\tstatus\tlarge_counters\tbig_blocks\tblocks\ttape\n')
        for res in pool.map(lambda m: run(m, sim_time), ms):
            row = fmt(res)
            f.write('\t'.join(row) + '\n')
            f.flush()
            print('\t'.join(row[:5]), flush=True)


if __name__ == '__main__':
    mp.freeze_support()
    main()
