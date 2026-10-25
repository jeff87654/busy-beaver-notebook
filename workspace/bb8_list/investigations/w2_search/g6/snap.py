"""snap.py: literal run from a token configuration printing tape snapshots.
usage: python snap.py MACHINE "tokens" [--far BITS] [--at s1,s2,..] [--every-slot E0] [--max N] [--maxsnap N]
Positions relative to the first input bit; tape printed from leftmost-visited to rightmost."""
import sys, argparse
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_champ35_1RB0RA_1LC0RH')
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/g6')
from tmlit import Sim
from g6lib import expand, word_of_tokens
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('tokens')
ap.add_argument('--far', default=''); ap.add_argument('--at', default=''); ap.add_argument('--slot', default='')
ap.add_argument('--max', type=int, default=10**7); ap.add_argument('--maxsnap', type=int, default=20); ap.add_argument('--suf', default='1010')
ap.add_argument('--lo', type=int, default=None); ap.add_argument('--hi', type=int, default=None)
a = ap.parse_args()
word = a.far + word_of_tokens(expand(a.tokens)) + a.suf
s = Sim.from_word(a.machine, word, len(word), 'G', size=1 << 22)
base = s.pos - len(word)
at = set(int(x) for x in a.at.split(',') if x)
slots = set(a.slot.split(',')) if a.slot else set()
ST = 'ABCDEFGHIJKLMNOP'
n = 0
def show(tag):
    lo = s.lo if a.lo is None else base + a.lo; hi = s.hi if a.hi is None else base + a.hi
    t = ''.join(('[' + str(s.tape[i]) + ']') if i == s.pos else str(s.tape[i]) for i in range(lo, hi + 1))
    print(f'{tag} step={s.steps} {ST[s.state]}{s.tape[s.pos]} pos={s.pos-base} lo={lo-base}: {t}')
while s.steps < a.max:
    sl = ST[s.state] + str(s.tape[s.pos])
    if s.steps in at or sl in slots:
        show('S'); n += 1
        if n >= a.maxsnap: break
    if not s.step():
        show('HALT'); break
