import sys
from kev import run_events
N = int(sys.argv[1]); lim = int(sys.argv[2])
words = []
def cb(steps, xs, w):
    words.append((steps, w)); return len(words) > lim
run_events(N, cb)
def toks(w):
    # pairs from the right end
    r = w[::-1]
    out = []
    i = 0
    while i + 1 < len(r):
        p = r[i:i+2]
        out.append({'11': 'S', '01': 'A', '10': 'a', '00': 'z'}[p]); i += 2
    rest = r[i:]
    return ''.join(out) + ('|' + rest if rest else '|')
for steps, w in words:
    print(steps, toks(w))
