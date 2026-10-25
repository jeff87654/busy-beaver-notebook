"""Literal check of the halting end and the sigma / step formulas on small odd k:
Y(k,2) = 0^inf 10 (1110)^k 11 (10)^2 E> 0^inf, k odd -> k digits -> Y(0,N), N odd -> m = 3N+7 even -> halt.
sigma = (9N+29)/2 = (261*9^k + 115)/16 ; steps = sum D(n_i) + pre(N) + RE(j), j = (m-2)/2.
Also the even-k continuation: Y(0,2) (k = 0) -> (10)^13 -> Y(6,2) is covered by trajectory.js."""
import sys
from lit import parse, MAIN, ST
TM = parse(MAIN)
def D(n): return 120 * n * n + 400 * n + 344
def pre(n): return 12 * n * n + 70 * n + 101
def RE(j): return 10 * j + 25
def run(word, cap=10**9):
    size = 4 * len(word) + (1 << 16)
    tape = bytearray(size); off = 16
    for i, c in enumerate(word): tape[off + i] = int(c)
    pos, q, steps = off + len(word), ST.index('E'), 0
    T = TM
    while steps < cap:
        e = T[q][tape[pos]]
        if e is None:
            return steps, sum(tape), ST[q], tape[pos], min(i for i in range(size) if tape[i]) - off
        w, d, q = e; tape[pos] = w; pos += d; steps += 1
        if pos >= size - 1:
            tape += bytearray(size); size *= 2
        assert pos > 0
    raise RuntimeError('cap')
ks = [int(x) for x in sys.argv[1:]] or [1, 3]
for k in ks:
    steps, ones, q, s, lo = run('10' + '1110' * k + '11' + '1010')
    n, tot = 2, 0
    for _ in range(k): tot += D(n); n = 9 * n + 13
    m = 3 * n + 7; j = (m - 2) // 2
    tot += pre(n) + RE(j)
    sig = (261 * 9**k + 115) // 16
    assert (261 * 9**k + 115) % 16 == 0
    print('Y(%d,2): N = %d, m = %d; halts in state %s reading %d after %d steps (predicted %d); ones %d (predicted %d); '
          'leftmost 1 at cell %d (start word at 0)' % (k, n, m, q, s, steps, tot, ones, sig, lo))
    assert steps == tot and ones == sig and q == 'H' and s == 1
print('OK')
