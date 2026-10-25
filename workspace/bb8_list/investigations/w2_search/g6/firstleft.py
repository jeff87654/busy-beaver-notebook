"""firstleft.py: run from a token config; print the reads at cells left of the initial leftmost 1 (first N of them),
with a tape window. usage: python firstleft.py MACHINE "tokens" [--far BITS] [--n 40]"""
import sys, argparse
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_champ35_1RB0RA_1LC0RH')
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/g6')
from tmlit import Sim
from g6lib import expand, word_of_tokens
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('tokens')
ap.add_argument('--far', default=''); ap.add_argument('--n', type=int, default=40); ap.add_argument('--max', type=int, default=10**8)
ap.add_argument('--edge', type=int, default=0, help='report reads at pos < edge (relative to word start)')
a = ap.parse_args()
word = a.far + word_of_tokens(expand(a.tokens)) + '1010'
s = Sim.from_word(a.machine, word, len(word), 'G', size=1 << 22)
base = s.pos - len(word); ST = 'ABCDEFGHIJKLMNOP'; k = 0
while s.steps < a.max and k < a.n:
    p = s.pos - base
    if p < a.edge:
        w = ''.join(('[' + str(s.tape[i]) + ']') if i == s.pos else str(s.tape[i]) for i in range(s.pos - 12, s.pos + 25))
        print(f'step={s.steps} {ST[s.state]}{s.tape[s.pos]} pos={p}  {w}'); k += 1
    if not s.step():
        print('HALT', s.steps, ST[s.state]); break
