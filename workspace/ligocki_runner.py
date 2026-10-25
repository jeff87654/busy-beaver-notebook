"""Run unmodified upstream Quick_Sim in a bounded subprocess on Windows.

Examples:
  python ligocki_runner.py --machine 1RB1LB_1LA1RZ --output quick.json
  python ligocki_runner.py --input holdouts.txt --workers 2 --timeout 20

The downloaded source uses Time_Limit.py (threading.Timer); its obsolete
Alarm.py has no active importers. This wrapper does not stub alarms or
change any simulator/prover code. External process timeouts are cutoffs,
never proofs of nonhalting. Upstream errors are kept separate from cutoffs.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import contextlib
import hashlib
import io
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parent
CODE = ROOT / 'third_party' / 'ligocki' / 'Code'
DEPS = ROOT / 'third_party' / 'runtime_deps'


class TailLog(io.TextIOBase):
    """Bound diagnostic memory while preserving the final upstream output."""
    def __init__(self, limit=60000):
        self.tail = ''
        self.limit = limit
        self.total_chars = 0

    def write(self, value):
        self.total_chars += len(value)
        self.tail = (self.tail + value)[-self.limit:]
        return len(value)

    def flush(self):
        pass


def count_value(value):
    """Keep exact decimal/symbolic counts distinct from approximations."""
    from NatExpr import approx_str
    if value is None:
        return None
    if type(value).__name__ == 'ConstInt':
        value = value.val
    if isinstance(value, int):
        if value.bit_length() <= 12000:
            return {'kind':'integer', 'decimal':str(value)}
        return {'kind':'large_integer', 'bit_length':value.bit_length(),
                'approximate':approx_str(value),
                'exact_value_omitted':True}
    expression = str(value)
    result = {'kind':'symbolic_expression', 'expression':expression[:200000],
              'expression_truncated':len(expression)>200000}
    try:
        result['approximate'] = approx_str(value)
    except Exception as exc:
        result['approximation_error'] = str(exc)
    return result


def child(payload):
    sys.path[:0] = [str(CODE), str(DEPS)]
    machine = payload['machine']
    argv = [str(CODE/'Quick_Sim.py'), '--quiet',
            '--max-loops', str(payload['max_loops']),
            '--bf-loops', str(payload['bf_loops'])]
    if payload['block_size']:
        argv += ['--block-size',str(payload['block_size'])]
    if payload['recursive']:
        argv += ['--recursive']
    if payload['no_backsymbol']:
        argv += ['--no-backsymbol']
    if payload['no_prover']:
        argv += ['--no-prover']
    argv += [machine]
    sys.argv = argv
    log = TailLog()
    start = time.monotonic()
    result = {'machine':machine, 'engine':'Ligocki Quick_Sim (unmodified)',
              'options':{k:v for k,v in payload.items() if k!='machine'}}
    try:
        if payload.get('sim_time'):
            # Optional in-process time limit. It wraps Simulator.step only, and the
            # simulator/prover code is unchanged. Past the deadline the next step marks the
            # run TIME_OUT, so the loop exits cleanly and the tape counts are still reported.
            # The budget starts at the first step, so imports and block finding are excluded
            # (setup_seconds reports those separately).
            from Macro import Simulator as _Sim, Turing_Machine as _TM
            _clock = {}
            _orig_step = _Sim.Simulator.step
            def _timed_step(self):
                now = time.monotonic()
                if 'deadline' not in _clock:
                    _clock['setup'] = now - start
                    _clock['deadline'] = now + payload['sim_time']
                if self.op_state == _TM.RUNNING and now > _clock['deadline']:
                    self.op_state = _TM.TIME_OUT
                    return
                return _orig_step(self)
            _Sim.Simulator.step = _timed_step
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            scope = runpy.run_path(str(CODE/'Quick_Sim.py'),run_name='__main__')
            sim = scope['sim']
            from Macro import Turing_Machine
            import io_pb2
            operation = sim.op_state
            if operation == Turing_Machine.HALT:
                status, reason = 'halt', 'explicit_halting_transition'
            elif operation == Turing_Machine.INF_REPEAT:
                status, reason = 'infinite', io_pb2.InfReason.Name(sim.inf_reason)
            elif operation == Turing_Machine.UNDEFINED:
                status, reason = 'undefined', 'undefined_transition'
            elif operation == Turing_Machine.OVER_STEPS_IN_MACRO:
                status, reason = 'cutoff', 'base_steps_in_macro_limit'
            elif operation == Turing_Machine.TIME_OUT:
                status, reason = 'cutoff', 'upstream_time_limit'
            elif operation == Turing_Machine.RUNNING:
                status, reason = 'cutoff', 'simulation_loop_limit'
            else:
                status, reason = 'error', 'unrecognized_simulator_state'
            result.update(status=status, reason=reason, upstream_state=operation,
                          loops=sim.num_loops,
                          steps=count_value(sim.step_num) if sim.compute_steps else None,
                          ones=count_value(sim.get_nonzeros()),
                          rule_moves=sim.num_rule_moves,
                          chain_moves=sim.num_chain_moves,
                          macro_moves=sim.num_macro_moves)
            if sim.prover:
                result['rules_proven'] = sim.prover.num_rules
                result['failed_proofs'] = sim.prover.num_failed_proofs
    except BaseException as exc:
        result.update(status='error',reason=type(exc).__name__,error=str(exc),
                      traceback=traceback.format_exc())
    result['elapsed_seconds'] = time.monotonic()-start
    if payload.get('sim_time') and '_clock' in locals():
        result['setup_seconds'] = _clock.get('setup')
    result['upstream_log_tail'] = log.tail
    result['upstream_log_truncated'] = log.total_chars > log.limit
    return result


def run_machine(machine, timeout=15, max_loops=10000, block_size=0,
                bf_loops=1000, recursive=False, no_backsymbol=False,
                no_prover=False, sim_time=0):
    """Return one structured outcome; each invocation gets a fresh process."""
    if timeout <= 0 or max_loops <= 0:
        raise ValueError('timeout and max_loops must be positive')
    if not re.fullmatch(r'(?:[01][LR][A-Z]|---){2}(?:_(?:[01][LR][A-Z]|---){2})*', machine):
        raise ValueError('Expected a standard binary TM transition table')
    states = len(machine.split('_'))
    for row in machine.split('_'):
        for offset in (0,3):
            target = row[offset+2]
            if row[offset:offset+3] != '---' and target != 'Z' and ord(target)-65 >= states:
                raise ValueError('Transition references a nonexistent state')
    payload = dict(machine=machine,max_loops=max_loops,block_size=block_size,
                   bf_loops=bf_loops,recursive=recursive,
                   no_backsymbol=no_backsymbol,no_prover=no_prover,sim_time=sim_time)
    start = time.monotonic()
    try:
        process = subprocess.run([sys.executable,str(Path(__file__).resolve()),'--_child'],
            input=json.dumps(payload),stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            encoding='utf-8',errors='replace',cwd=str(ROOT),timeout=timeout,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    except subprocess.TimeoutExpired:
        return {'machine':machine,'status':'cutoff','reason':'external_wall_timeout',
                'timeout_seconds':timeout,'elapsed_seconds':time.monotonic()-start,
                'options':payload,'engine':'Ligocki Quick_Sim (unmodified)'}
    try:
        result = json.loads(process.stdout)
    except (ValueError,TypeError):
        result = {'machine':machine,'status':'error','reason':'invalid_child_output',
                  'stdout_tail':process.stdout[-60000:],
                  'stderr_tail':process.stderr[-60000:]}
    result['process_returncode'] = process.returncode
    result['wall_seconds'] = time.monotonic()-start
    if process.returncode != 0:
        result['status'] = 'error'
        result['reason'] = 'child_process_failure'
    return result


def load_machines(path):
    text = Path(path).read_text(encoding='utf-8-sig')
    if Path(path).suffix.lower() not in ('.json','.jsonl'):
        return [line.split()[0] for line in text.splitlines()
                if line.strip() and not line.lstrip().startswith('#')]
    data = ([json.loads(line) for line in text.splitlines() if line.strip()]
            if Path(path).suffix.lower()=='.jsonl' else json.loads(text))
    if isinstance(data,dict):
        data = data.get('machines',data.get('results',data.get('unresolved',[])))
    machines = []
    for row in data:
        if isinstance(row,str):
            machines.append(row)
        elif isinstance(row,dict):
            machines.append(row.get('machine',row.get('tm')))
        elif isinstance(row,list):
            machines.append(row[-1])
    if any(not isinstance(m,str) for m in machines):
        raise ValueError('Input contains a row without a machine string')
    return machines


def main():
    if sys.argv[1:]==['--_child']:
        result = child(json.load(sys.stdin))
        sys.stdout.write(json.dumps(result,ensure_ascii=True)+'\n')
        return
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--machine',action='append',default=[])
    parser.add_argument('--input')
    parser.add_argument('--output',default='ligocki_results.json')
    parser.add_argument('--workers',type=int,default=1)
    parser.add_argument('--timeout',type=float,default=15)
    parser.add_argument('--max-loops',type=int,default=10000)
    parser.add_argument('--block-size',type=int,default=0)
    parser.add_argument('--bf-loops',type=int,default=1000)
    parser.add_argument('--recursive',action='store_true')
    parser.add_argument('--no-backsymbol',action='store_true')
    parser.add_argument('--no-prover',action='store_true')
    parser.add_argument('--sim-time',type=float,default=0,
                        help='in-process time limit (s); reports counts reached (reason upstream_time_limit)')
    args = parser.parse_args()
    machines = args.machine + (load_machines(args.input) if args.input else [])
    machines = list(dict.fromkeys(machines))
    if not machines:
        parser.error('Provide --machine or --input')
    if not 1 <= args.workers <= 16:
        parser.error('--workers must be between 1 and 16')
    options = {k:getattr(args,k) for k in ('timeout','max_loops','block_size','bf_loops',
                                         'recursive','no_backsymbol','no_prover','sim_time')}
    hashes = {name:hashlib.sha256((CODE/name).read_bytes()).hexdigest()
              for name in ('Quick_Sim.py','Macro/Simulator.py','Macro/Proof_System.py',
                           'Macro/Turing_Machine.py','Time_Limit.py')}
    output = {'configuration':vars(args),'source_sha256':hashes,
              'source_modified':False,'results':[]}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_machine,machine,**options):machine for machine in machines}
        for future in as_completed(futures):
            result = future.result()
            output['results'].append(result)
            Path(args.output).write_text(json.dumps(output,indent=2),encoding='utf-8')
            print(json.dumps({k:v for k,v in result.items()
                              if k not in ('upstream_log_tail','traceback','options')},
                             ensure_ascii=True),flush=True)


if __name__=='__main__':
    main()
