"""Ligocki's Quick_Sim machinery (unmodified library) started from an arbitrary configuration.

  python qs_from.py MACHINE WORD HEAD STATE [--block-size K] [--backsymbol] [--max-loops N] [--print-loops P]
         [--max-num-reps R] [--no-recursive] [--exp-linear-rules]

WORD is a 0/1 word, HEAD the head index into it (len(WORD) = the blank just right of it), STATE a letter.
The word is padded with blanks to block boundaries (block 0 starts at WORD[HEAD]).
"""
from __future__ import annotations

import sys
import time
from optparse import OptionParser
from pathlib import Path

LIG = Path(__file__).resolve().parents[3] / 'third_party' / 'ligocki' / 'Code'
sys.path.insert(0, str(LIG))
import IO  # noqa: E402
from NatExpr import InfNat, approx_and_full_str  # noqa: E402
from Macro import Block_Finder, Simulator, Turing_Machine, Tape  # noqa: E402


def main():
    p = OptionParser()
    p.add_option('--max-loops', type=int, default=100000)
    p.add_option('--print-loops', type=int, default=10000)
    p.add_option('--max-steps-in-block', type=int, default=1_000_000)
    p.add_option('--max-steps-in-backsymbol', type=int, default=1_000)
    Simulator.add_option_group(p)
    Block_Finder.add_option_group(p)
    opts, args = p.parse_args()
    mstr, word, head, st = args[0], args[1], int(args[2]), args[3]
    if word == '-':
        word = ''
    base = IO.get_tm(mstr)
    k = opts.block_size or 1
    machine = base
    if k != 1:
        machine = Turing_Machine.Block_Macro_Machine(base, k, max_sim_steps_per_symbol=opts.max_steps_in_block)
    if opts.backsymbol:
        machine = Turing_Machine.Backsymbol_Macro_Machine(machine, max_sim_steps_per_symbol=opts.max_steps_in_backsymbol)
    sim = Simulator.Simulator(machine, opts)
    left, right = word[:head], word[head:]
    left = '0' * ((-len(left)) % k) + left
    right = right + '0' * ((-len(right)) % k)
    if opts.backsymbol and not left:
        left = '0' * k

    def blk(s):
        t = tuple(int(c) for c in s)
        return t[0] if k == 1 else Turing_Machine.Block_Symbol(t)

    lb = [blk(left[i:i + k]) for i in range(0, len(left), k)]
    rb = [blk(right[i:i + k]) for i in range(0, len(right), k)]
    zero = machine.init_symbol
    back = None
    if opts.backsymbol:
        back = lb.pop()
    t0 = [Tape.Repeated_Symbol(zero, InfNat())]
    for s in lb:
        if t0[-1].symbol == s:
            t0[-1].num += 1
        else:
            t0.append(Tape.Repeated_Symbol(s, 1))
    t1 = [Tape.Repeated_Symbol(zero, InfNat())]
    for s in reversed(rb):
        if t1[-1].symbol == s:
            t1[-1].num += 1
        else:
            t1.append(Tape.Repeated_Symbol(s, 1))
    sim.tape.tape = [t0, t1]
    sim.tape.dir = Turing_Machine.RIGHT
    sim.dir = Turing_Machine.RIGHT
    q = Turing_Machine.Simple_Machine_State(ord(st) - 65)
    sim.state = Turing_Machine.Backsymbol_Macro_Machine_State(q, back) if opts.backsymbol else q
    t = time.time()
    print('start:', sim.tape.print_with_state(sim.state))
    while sim.op_state == Turing_Machine.RUNNING and sim.num_loops < opts.max_loops:
        sim.loop_run(opts.print_loops)
        print(f'loops {sim.num_loops} steps {approx_and_full_str(sim.step_num) if opts.compute_steps else "-"} '
              f'{time.time() - t:.1f}s rules {sim.prover.num_rules if sim.prover else 0}')
        print('   ', sim.tape.print_with_state(sim.state))
        sys.stdout.flush()
    print('op_state', sim.op_state, sim.op_details)
    if sim.op_state in (Turing_Machine.HALT, Turing_Machine.UNDEFINED):
        print('HALT steps', approx_and_full_str(sim.step_num) if opts.compute_steps else '-', 'nonzeros',
              approx_and_full_str(sim.get_nonzeros()))


if __name__ == '__main__':
    main()
