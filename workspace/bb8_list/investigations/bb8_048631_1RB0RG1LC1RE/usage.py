"""Transition usage of a machine from the blank tape (exact literal simulation).

    python usage.py TM N [TM2 ...]      -> for each TM: count per transition in N steps, and the step of the
                                          last use of each transition (so 'used only in the first 40 steps'
                                          is visible at once).
"""
import sys
from tmlit import Sim, ST


def usage(tm, N):
    s = Sim(tm, size=1 << 20)
    cnt = {}
    last = {}
    first = {}
    halted = False
    T = s.T
    tape = s.tape
    while s.steps < N:
        key = (s.state, s.tape[s.pos])
        if not s.step():
            halted = True
            break
        cnt[key] = cnt.get(key, 0) + 1
        last[key] = s.steps
        first.setdefault(key, s.steps)
    return cnt, first, last, halted, s


def main():
    N = int(sys.argv[2])
    for tm in [sys.argv[1]] + sys.argv[3:]:
        cnt, first, last, halted, s = usage(tm, N)
        print(tm, 'HALTED at %d' % s.steps if halted else 'ran %d steps' % s.steps)
        for q in range(8):
            for sym in (0, 1):
                e = tm.split('_')[q][3 * sym:3 * sym + 3]
                k = (q, sym)
                print('  %s%d %s  count %12d  first %10s  last %10s' % (
                    ST[q], sym, e, cnt.get(k, 0), first.get(k, '-'), last.get(k, '-')))


if __name__ == '__main__':
    main()
