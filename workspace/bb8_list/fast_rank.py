"""Growth ranking with persistent Quick_Sim workers (no per-machine process launch).

Each worker imports Ligocki's code once, then runs Quick_Sim.py (unmodified, via runpy)
on one machine at a time. The settings are those of ../ligocki_runner.py with
--recursive --max-loops 1000000 and a budget of T CPU-seconds (not wall-clock, so scores
do not depend on machine load). The budget starts at the first simulation step; a machine still running then stops cleanly, and its counts are reported
(reason upstream_time_limit). A worker exceeding --hard-timeout on one machine is
terminated and replaced (reason external_wall_timeout). Workers are recycled every
--recycle machines. Output rows match ligocki_runner.py results.

Must run under the venv interpreter (gmpy2/protobuf):
  ../third_party/venv311/Scripts/python.exe fast_rank.py --input H.txt --output out.json --workers 4
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import multiprocessing as mp
import multiprocessing.connection
import runpy
import sys
import time
import traceback
from pathlib import Path

import psutil

PROJECT = Path(__file__).resolve().parent.parent
CODE = PROJECT / 'third_party' / 'ligocki' / 'Code'


def _worker(conn, sim_time, max_loops):
    sys.path[:0] = [str(CODE), str(PROJECT)]
    from Macro import Simulator as Sim, Turing_Machine as TM
    import io_pb2
    from ligocki_runner import count_value
    clock = {}
    orig_step = Sim.Simulator.step

    def timed_step(self):
        now = time.process_time()  # CPU time: the budget is independent of machine load
        if 'deadline' not in clock:
            clock['setup'] = now - clock['start']
            clock['deadline'] = now + sim_time
        if self.op_state == TM.RUNNING and now > clock['deadline']:
            self.op_state = TM.TIME_OUT
            return
        return orig_step(self)
    Sim.Simulator.step = timed_step

    while True:
        machine = conn.recv()
        if machine is None:
            return
        clock.clear()
        clock['start'] = time.process_time()
        wall0 = time.monotonic()
        result = {'machine': machine, 'engine': 'Ligocki Quick_Sim (unmodified), persistent worker',
                  'options': {'recursive': True, 'max_loops': max_loops, 'sim_time': sim_time}}
        sys.argv = [str(CODE / 'Quick_Sim.py'), '--quiet', '--max-loops', str(max_loops),
                    '--bf-loops', '1000', '--recursive', machine]
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                sim = runpy.run_path(str(CODE / 'Quick_Sim.py'), run_name='__main__')['sim']
            op = sim.op_state
            if op == TM.HALT:
                status, reason = 'halt', 'explicit_halting_transition'
            elif op == TM.INF_REPEAT:
                status, reason = 'infinite', io_pb2.InfReason.Name(sim.inf_reason)
            elif op == TM.UNDEFINED:
                status, reason = 'undefined', 'undefined_transition'
            elif op == TM.OVER_STEPS_IN_MACRO:
                status, reason = 'cutoff', 'base_steps_in_macro_limit'
            elif op == TM.TIME_OUT:
                status, reason = 'cutoff', 'upstream_time_limit'
            elif op == TM.RUNNING:
                status, reason = 'cutoff', 'simulation_loop_limit'
            else:
                status, reason = 'error', 'unrecognized_simulator_state'
            result.update(status=status, reason=reason, loops=sim.num_loops,
                          steps=count_value(sim.step_num) if sim.compute_steps else None,
                          ones=count_value(sim.get_nonzeros()))
            if sim.prover:
                result['rules_proven'] = sim.prover.num_rules
        except BaseException as exc:  # noqa: BLE001 - report, keep the worker alive
            result.update(status='error', reason=type(exc).__name__, error=str(exc)[:2000],
                          traceback=traceback.format_exc()[-4000:])
        result['elapsed_seconds'] = time.process_time() - clock['start']  # CPU seconds
        result['wall_seconds'] = time.monotonic() - wall0
        result['setup_seconds'] = clock.get('setup')
        conn.send(result)


class Pool:
    def __init__(self, workers=4, sim_time=2.0, max_loops=1_000_000, hard_timeout=60.0, recycle=200,
                 wall_backstop=3600.0):
        self.ctx = mp.get_context('spawn')
        self.n, self.sim_time, self.max_loops = workers, sim_time, max_loops
        # hard_timeout is in CPU seconds of the worker, so a starved (idle-priority) worker is not
        # mistaken for a stuck one; wall_backstop is an absolute wall-clock limit.
        self.hard_timeout, self.recycle, self.wall_backstop = hard_timeout, recycle, wall_backstop
        self.slots = [None] * workers

    def _spawn(self, i):
        parent, child = self.ctx.Pipe()
        proc = self.ctx.Process(target=_worker, args=(child, self.sim_time, self.max_loops), daemon=True)
        proc.start()
        self.slots[i] = {'proc': proc, 'conn': parent, 'done': 0, 'job': None, 't': 0.0, 'cpu0': 0.0,
                         'ps': psutil.Process(proc.pid)}

    @staticmethod
    def _cpu(s):
        try:
            t = s['ps'].cpu_times()
            return t.user + t.system
        except psutil.Error:
            return float('inf')

    def _kill(self, i):
        s = self.slots[i]
        if s:
            with contextlib.suppress(Exception):
                s['proc'].kill()
                s['proc'].join(5)
        self.slots[i] = None

    def rank(self, machines):
        todo = list(dict.fromkeys(machines))[::-1]
        results = []
        while todo or any(s and s['job'] for s in self.slots):
            for i in range(self.n):
                s = self.slots[i]
                if s is None:
                    self._spawn(i)
                    s = self.slots[i]
                if s['job'] is None and todo:
                    s['job'], s['t'] = todo.pop(), time.monotonic()
                    s['cpu0'] = self._cpu(s)
                    s['conn'].send(s['job'])
            ready = mp.connection.wait([s['conn'] for s in self.slots if s and s['job']], timeout=1.0)
            for i, s in enumerate(self.slots):
                if not s or not s['job']:
                    continue
                if s['conn'] in ready:
                    try:
                        results.append(s['conn'].recv())
                    except EOFError:
                        results.append({'machine': s['job'], 'status': 'error', 'reason': 'worker_died'})
                        self._kill(i)
                        continue
                    s['job'] = None
                    s['done'] += 1
                    if s['done'] >= self.recycle:
                        with contextlib.suppress(Exception):
                            s['conn'].send(None)
                        self._kill(i)
                elif (self._cpu(s) - s['cpu0'] > self.hard_timeout
                      or time.monotonic() - s['t'] > self.wall_backstop or not s['proc'].is_alive()):
                    results.append({'machine': s['job'], 'status': 'cutoff', 'reason': 'external_cpu_timeout',
                                    'timeout_cpu_seconds': self.hard_timeout,
                                    'cpu_seconds': self._cpu(s) - s['cpu0'],
                                    'wall_seconds': time.monotonic() - s['t']})
                    self._kill(i)
        return results

    def close(self):
        for i in range(self.n):
            s = self.slots[i]
            if s:
                with contextlib.suppress(Exception):
                    s['conn'].send(None)
            self._kill(i)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--sim-time', type=float, default=2.0)
    ap.add_argument('--hard-timeout', type=float, default=60.0, help='CPU seconds per machine')
    a = ap.parse_args()
    machines = [l.split()[0] for l in Path(a.input).read_text().splitlines() if '_' in l]
    pool = Pool(a.workers, a.sim_time, hard_timeout=a.hard_timeout)
    t = time.time()
    try:
        res = pool.rank(machines)
    finally:
        pool.close()
    Path(a.output).write_text(json.dumps({'configuration': vars(a), 'results': res}, indent=1))
    print(f'{len(res)} machines in {time.time()-t:.1f}s')


if __name__ == '__main__':
    main()
