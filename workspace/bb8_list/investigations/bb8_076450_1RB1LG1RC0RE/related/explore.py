"""Run from 0^inf A>0 <word> 0^inf and print successive left-edge A0 configs (with offset of head
relative to the start head position), stopping after N events, on halt, or on step limit.
usage: python explore.py TM word N [maxsteps]"""
import sys
from lit import Sim, compress, ST

def run(tm, word, N=20, maxsteps=10**7, show=True, skipO=True):
    s = Sim(tm, size=max(1 << 12, 8 * len(word) + 4096))
    base = s.pos
    for i, c in enumerate(word):
        s.tape[base + 1 + i] = int(c)
    s.hi = base + len(word)
    ev = []
    while s.steps < maxsteps and len(ev) < N:
        if not s.step():
            ev.append(('HALT', s.steps, s.pos - base, ST[s.state], s.show()))
            break
        if s.state == 0 and s.tape[s.pos] == 0 and s.pos <= s.lo and not any(s.tape[s.lo:s.pos]):
            hi = s.hi
            while hi > s.pos and s.tape[hi] == 0: hi -= 1
            w = ''.join(map(str, s.tape[s.pos+1:hi+1]))
            ev.append(('A0', s.steps, s.pos - base, w))
    return ev

if __name__ == '__main__':
    tm, word, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
    ms = int(sys.argv[4]) if len(sys.argv) > 4 else 10**7
    prev = None
    for e in run(tm, word, N, ms):
        if e[0] == 'HALT':
            print('HALT step', e[1], 'off', e[2], e[4])
        else:
            print(e[1], 'off', e[2], compress(e[3]))
