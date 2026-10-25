"""Probe the BB(8) record's exhaustion: run K(0^n;0;b) with E0 undefined, show the tape when E0 is reached,
and measure which (state,symbol) slots are used in each phase (start-up, R1-R3, R4 up to E0)."""
import sys
sys.path.insert(0, '../bb8_champ35_1RB0RA_1LC0RH')
from tmlit import Sim, ST
TM = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF'

def kword(ds, a, b):
    w = '1'
    for d in ds: w += '01' * (3 * d + 1) + '1'
    w += '01' * (3 * a + 1) + '1' + '01' * (3 * b + 1) + '10101'
    return w

def start(ds, a, b, tm=TM):
    w = kword(ds, a, b)
    return Sim.from_word(tm, '0000' + w + '0', 4 + len(w), 'G', size=1 << 18)

def show(s, pad=2):
    lo, hi = s.bounds()
    t = ''.join(str(x) for x in s.tape[lo:s.pos])
    u = ''.join(str(x) for x in s.tape[s.pos:hi + 1])
    return f'{t} {ST[s.state]}>{u}'

def run(ds, a, b, N=10**8, tm=TM):
    s = start(ds, a, b, tm)
    s.usage = {}
    while s.steps < N:
        if not s.step():
            return s
    return s

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'e0':
        for n in (1, 2, 3, 5):
            for b in (0, 1, 2, 3):
                s = run([0] * n, 0, b)
                print(n, b, s.steps, s.last, show(s))
    elif mode == 'use':
        # usage in R1-R3 on assorted configurations: stop when K reappears
        pass
