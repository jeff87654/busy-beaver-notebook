"""Literal successor of K(ds; a; b): run from the K word, state C on the right blank, until the next K event."""
import sys
from kev import run_events, parse_K, fmt

def kword(ds, a, b):
    xs = list(ds) + [a, b]
    return '1' + ''.join('10' * x + '11' for x in xs)

def succ(ds, a, b, cap=2_000_000):
    """returns ('K', steps, xs) | ('HALT', steps) | ('T', cap)"""
    w = kword(ds, a, b)
    res = []
    first = [True]
    def cb(steps, xs, word):
        if steps == 0: return False      # the initial configuration itself
        if xs is not None:
            res.append((steps, xs)); return True
        return False
    r = run_events(cap, cb, init=(w, len(w), 2))
    if r[0] == 'HALT': return ('HALT', r[1])
    if r[0] == 'STOP': return ('K', res[0][0], res[0][1])
    return ('T', cap)

def show(r):
    if r[0] == 'K': return '%d steps -> %s' % (r[1], fmt(r[2]))
    return str(r)

if __name__ == '__main__':
    ds = eval(sys.argv[1]); a = int(sys.argv[2]); b = int(sys.argv[3])
    cap = int(sys.argv[4]) if len(sys.argv) > 4 else 2_000_000
    print(show(succ(ds, a, b, cap)))
