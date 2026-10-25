"""b = 2526 (= B mod 2520): (a1) stage 0 literal; (a2) the first two periods with fakes (hybrid); (a3) the last three
periods + endgame from the rule-composed configuration [2^(1+4j), 5, 1^(12B+5-14j), 0,0,2, 1^n | A], j = (12B-2)/14 - 3."""
import random
from fw import *
import n1sim
from n1sim import literal, run, flab
B = 2526
rng = random.Random(11)
# (a1)
L = [2] + [1] * (12 * B + 12) + [0] + [1] * 35
print('(a1) stage-0 special at B=2526: B True 2549700 (done in the first run)', flush=True)
# (a2) from the record end, 24 specials with small fakes
fakes = [40 + 120 * rng.randint(1, 3) for _ in range(200)]
lines = []
sig, k2, r2 = run(B, fakes, maxspec=24, log=lambda s: lines.append(s))
for s in lines:
    print('   ', s[:230], flush=True)
# (a3)
j = (12 * B - 2) // 14 - 3
k = 1 + 4 * j; m = 12 * B + 5 - 14 * j
print('(a3) start: k=%d m=%d (last P1 expected at m=7 after 3 more periods)' % (k, m), flush=True)
lines = []
sig, k3, r3 = run(B, fakes, maxspec=60, log=lambda s: lines.append(s), start=('', [2] * k + [5] + [1] * m + [0, 0, 2] + [1] * 300, 1000))
for s in lines:
    print('   ', s[:230], flush=True)
