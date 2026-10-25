"""qs_from.py MACHINE RUNSPEC [--k 2] [--loops N] [--every SEC] [--maxprint 400] [--recursive]
Run Ligocki's Quick_Sim (macro machine + prover) from a custom tape: run-spec word, head in state B on the blank cell
right of the word (B-frontier).  Prints the tape (base-level runs; big reps symbolic) every --every seconds."""
import sys, os, time, argparse
LIG = r"C:\Users\jeffr\Downloads\bb8\third_party\ligocki\Code"
sys.path.insert(0, LIG)
from Macro import Simulator, Turing_Machine, Tape
from Macro.Turing_Machine import Block_Macro_Machine, Backsymbol_Macro_Machine, Backsymbol_Macro_Machine_State, Block_Symbol, Simple_Machine_State
import IO
from NatExpr import InfNat
from trace import word as spec_word

def build(ms, spec, k, recursive, state='B'):
    base = IO.get_tm(ms)
    w = spec_word(spec)
    pad = (-len(w)) % k
    w = '0'*pad + w
    blocks = [Block_Symbol(tuple(int(c) for c in w[i:i+k])) for i in range(0, len(w), k)]
    m = Block_Macro_Machine(base, k) if k > 1 else base
    m = Backsymbol_Macro_Machine(m)
    opts = Simulator.create_default_options()
    opts.recursive = recursive
    opts.compute_steps = True
    sim = Simulator.Simulator(m, opts)
    blank = m.init_symbol if k == 1 else Block_Symbol((0,)*k)
    if k == 1:
        blocks = [int(c) for c in w]; blank = 0
    left = [Tape.Repeated_Symbol(blank, InfNat())]
    for b in blocks[:-1]:
        if left[-1].symbol == b and not isinstance(left[-1].num, InfNat): left[-1].num += 1
        else: left.append(Tape.Repeated_Symbol(b, 1))
    sim.tape.tape = [left, [Tape.Repeated_Symbol(blank, InfNat())]]
    sim.tape.dir = Turing_Machine.RIGHT
    sim.state = Backsymbol_Macro_Machine_State(Simple_Machine_State(ord(state)-65), blocks[-1])
    return sim

def tape_str(sim, maxlen=400):
    s = sim.tape.print_with_state(sim.state)
    return s if len(s) <= maxlen else s[:maxlen//2] + ' ... ' + s[-maxlen//2:]

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('machine'); ap.add_argument('spec')
    ap.add_argument('--k', type=int, default=2); ap.add_argument('--loops', type=int, default=10**6)
    ap.add_argument('--every', type=float, default=5.0); ap.add_argument('--maxprint', type=int, default=600)
    ap.add_argument('--recursive', action='store_true'); ap.add_argument('--chunk', type=int, default=1000)
    a = ap.parse_args()
    sim = build(a.machine, a.spec, a.k, a.recursive)
    print('start', tape_str(sim, a.maxprint)); sys.stdout.flush()
    t0 = time.time(); last = 0; loops = 0
    while sim.op_state == Turing_Machine.RUNNING and loops < a.loops:
        sim.loop_run(a.chunk); loops += a.chunk
        if time.time() - last >= a.every:
            last = time.time()
            print(f'[{time.time()-t0:7.1f}s loops={loops} steps~{str(sim.step_num)[:30]}] ', tape_str(sim, a.maxprint)); sys.stdout.flush()
    print('END op_state', sim.op_state, sim.op_details if sim.op_state != Turing_Machine.RUNNING else '')
    print('steps', str(sim.step_num)[:200])
    print(tape_str(sim, 4000))
