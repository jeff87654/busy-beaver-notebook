"""Literal check of the halting end and the sigma / step formulas on small even k:
Z(k,2) = 0^inf (1110)^k 11 (10)^2 E> 0^inf, k even -> k digits -> Z(0,N), N even -> m = 3N+4 even -> halt.
sigma = (9N+24)/2 = (261*9^k + 75)/16 ; steps = sum D(n_i) + pre(N) + 10j + 27, j = (m-2)/2."""
from lit import parse, MAIN, ST
TM = parse(MAIN)
def D(n): return 120 * n * n + 400 * n + 344
def pre(n): return 12 * n * n + 46 * n + 47
def run(word):
    tape = {i: int(c) for i, c in enumerate(word)}
    pos, q, steps = len(word), ST.index('E'), 0
    while True:
        e = TM[q][tape.get(pos, 0)]
        if e is None: return steps, sum(tape.values()), ST[q], tape.get(pos, 0)
        w, d, q = e; tape[pos] = w; pos += d; steps += 1
for k in (0, 2):
    steps, ones, q, s = run('1110' * k + '11' + '1010')
    n, tot = 2, 0
    for _ in range(k): tot += D(n); n = 9 * n + 13
    m = 3 * n + 4; j = (m - 2) // 2
    tot += pre(n) + 10 * j + 27
    sig = (261 * 9**k + 75) // 16
    print('Z(%d,2): halts in state %s reading %d after %d steps (predicted %d); ones %d (predicted %d)' %
          (k, q, s, steps, tot, ones, sig))
    assert steps == tot and ones == sig and q == 'H' and s == 1
print('OK')
