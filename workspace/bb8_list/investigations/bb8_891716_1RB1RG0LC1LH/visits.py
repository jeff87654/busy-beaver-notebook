import sys
from kev import run_events
N = int(sys.argv[1]); lim = int(sys.argv[2])
words = []
def cb(steps, xs, w):
    words.append((steps, w)); return len(words) > lim
run_events(N, cb)
prev = None
for steps, w in words:
    if prev is not None:
        pw = prev[1]
        i = 0
        while i < min(len(pw), len(w)) and pw[i] == w[i]: i += 1
        # back off to keep same suffix after common prefix
        print('%6d (+%4d) common=%d  [%s] -> [%s]' % (steps, steps - prev[0], i, pw[i:], w[i:]))
    prev = (steps, w)
