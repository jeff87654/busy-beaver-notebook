"""Build the BB(7) champion's E0-read configuration from K(0^11; 0; b) (follow2 default template, canonical state B).
usage: python mkstart.py b1 b2 ...  -> prints 'b<b> WORD HEAD E' lines (renum/grid start format); fails loudly."""
import sys
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_champ35_1RB0RA_1LC0RH')
from tmlit import Sim
BASE = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF'
def kword(b, n=11):
    return '11' + '101' * (n + 1) + '10' * (3 * b + 2) + '1' + '11001'
for b in map(int, sys.argv[1:]):
    w = kword(b)
    s = Sim.from_word(BASE, '0000' + w + '0', 4 + len(w), 'B', size=1 << 20)
    while s.step():
        pass
    assert s.last == (4, 0), f'base halted at {s.last}, not E0'
    lo, hi = s.bounds()
    word = ''.join(map(str, s.tape[lo:hi + 1]))
    print(f'b{b} {word} {s.pos - lo} E', file=sys.stdout)
    print(f'# b={b} steps={s.steps} ones={s.ones()} len={len(word)}', file=sys.stderr)
