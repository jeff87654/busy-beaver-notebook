"""Run a machine (any number of states) from a constructed list-exhausted configuration and show the tape.

  python watch_exhaust.py MACHINE N_ZEROS B MAXSTEPS [TEMPLATE]
      TEMPLATE default: the BB(7) champion's  R,B,P=11,u=10,s=1,d=3d+1,b=3b+2,S=111001

Prints the run-length compressed tape at 10^k steps (k = 3..) and at a halt, plus every family configuration of the
template that the run reaches (a rebuild), so a slow rebuild, a halt or a runaway can be told apart.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'bb8_champ35_vs_bb7'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'rebuilder_nbrs'))
from ligocki_notation import Sim, parse_tm  # noqa: E402
from r4grid import tmpl_from  # noqa: E402


def rle(s, maxlen=220):
    out = []
    for m in re.finditer(r'(10)+|(01)+|0+|1+', s):
        g = m.group(0)
        if len(g) >= 4 and (g.startswith('10') or g.startswith('01')) and set(g) == {'0', '1'}:
            out.append(f'({g[:2]})^{len(g) // 2}' + (g[-1] if len(g) % 2 else ''))
        else:
            out.append(g if len(g) < 4 else f'{g[0]}^{len(g)}')
    x = ' '.join(out)
    return x if len(x) <= maxlen else x[:maxlen] + ' ...'


def main():
    m, nz, b, maxsteps = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    tstr = sys.argv[5] if len(sys.argv) > 5 else 'R,B,P=11,u=10,s=1,d=3d+1,b=3b+2,S=111001'
    o, T = tmpl_from(tstr)
    assert o == 'R'
    word = T.build((0,) * nz, 0, b)
    sim = Sim(parse_tm(m), word, head=len(word), state=T.q)
    print(f'start K(0^{nz}; 0; {b}): {rle(word)}')
    fams = []

    def cb(step, s):
        k = T.parse(s)
        if k is not None and step > 0:
            fams.append((step, k))
            if len(fams) <= 5:
                print(f'  family config at step {step}: {len(k[0])} digits {k[0][:4]}..{k[0][-3:]}; a={k[1]}; b={k[2]}')

    checkpoint = 1000
    while sim.steps < maxsteps and not sim.halted:
        target = min(checkpoint, maxsteps)
        sim.run(target, T.q, cb)
        if sim.halted:
            break
        print(f'step {sim.steps:>11}: state {chr(65 + sim.state)}, {sim.ones()} ones, width {len(sim.tape_str())}: '
              f'{rle(sim.tape_str())}')
        checkpoint *= 10
    if sim.halted:
        print(f'HALT at step {sim.steps}, {sim.ones()} ones: {rle(sim.tape_str())}')
    print(f'{len(fams)} family configurations reached')


if __name__ == '__main__':
    main()
