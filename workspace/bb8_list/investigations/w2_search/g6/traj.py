"""traj.py: print every step in a step window [a, b] of a literal run from a token config (slot, pos, window)."""
import sys, argparse
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_champ35_1RB0RA_1LC0RH')
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/g6')
from tmlit import Sim
from g6lib import expand, word_of_tokens
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('tokens'); ap.add_argument('a', type=int); ap.add_argument('b', type=int)
ap.add_argument('--far', default=''); ap.add_argument('--lo', type=int, default=-20); ap.add_argument('--hi', type=int, default=40)
a = ap.parse_args()
word = a.far + word_of_tokens(expand(a.tokens)) + '1010'
s = Sim.from_word(a.machine, word, len(word), 'G', size=1 << 22)
base = s.pos - len(word); ST = 'ABCDEFGHIJKLMNOP'
while s.steps <= a.b:
    if s.steps >= a.a:
        w = ''.join(('[' + str(s.tape[i]) + ']') if i == s.pos else str(s.tape[i]) for i in range(base + a.lo, base + a.hi))
        print(f'{s.steps:8d} {ST[s.state]}{s.tape[s.pos]} {s.pos-base:5d} {w}')
    if not s.step():
        print('HALT'); break
