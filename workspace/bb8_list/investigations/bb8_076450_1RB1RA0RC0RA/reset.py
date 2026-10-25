"""Start from  L 000 1^m A>0  (L given as 0/1 string, blank to its left) and run until the next
configuration  ... 0 1^a 0 1 0 1 B>0 (right end, fresh b=1 start) ; print it as runs."""
import sys
from fromcfg import make, desc
from lit import ST
def run(L, m, N=10**7, tm=None):
    w = L + '000' + '1' * m
    kw = {} if tm is None else {'tm': tm}
    s = make('0' * 4 + w + '0', 4 + len(w), 'A', **kw)
    while s.steps < N:
        if not s.step():
            return 'HALT', s.steps, desc(s)[0]
        if s.state == 1 and s.tape[s.pos] == 0 and s.pos >= s.hi and s.tape[s.pos-1] == 1 and s.tape[s.pos-2] == 0 \
                and s.tape[s.pos-3] == 1 and s.tape[s.pos-4] == 0:
            return 'OK', s.steps, desc(s)[0]
    return 'TIMEOUT', s.steps, desc(s)[0]
if __name__ == '__main__':
    for L in sys.argv[1].split(','):
        for m in map(int, sys.argv[2].split(',')):
            print(repr(L), m, run(L, m))
