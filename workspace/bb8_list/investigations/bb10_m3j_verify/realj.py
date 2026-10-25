"""M3J whole chain in the real class: B = 366 (= B_real mod 600), fakes = 40 mod 120 in several orders; fit ones."""
import sys, random
from fractions import Fraction as F
from chain_j import run_chain
import osim
rng = random.Random(int(sys.argv[1]))
B = int(sys.argv[2])
rows = []
for t in range(int(sys.argv[3])):
    fk = [40 + 120 * rng.randint(2, 25) for _ in range(6)]
    sig, kind, ones, hq = run_chain(B, fk)
    print(B, fk, kind, hq, ones, flush=True)
