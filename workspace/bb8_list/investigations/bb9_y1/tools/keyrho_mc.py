# keyrho_mc.py : Monte Carlo of the C04 cascade orbit (sketch map g, parked consumption a) from L0 = 36B+73 with the
# true residue mod 5^8 and random higher digits; joint distribution of (key = first value < 60, P-consumption mod 5).
import random, sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from towermod import B_mod
C = {0: -100, 1: 32, 2: -46, 3: -64, 4: -52}; A = {0: 3, 1: 11, 2: 4, 3: 6, 4: 6}
K = 8; m = 5 ** K; base = (36 * B_mod(m) + 73) % m
# also keep L odd and 1 mod 3: L0 = 36B+73: B even, B = 0 mod 3 -> L0 = 73 mod 72*... use CRT with mod 6 residue 1
cnt = {}; random.seed(1)
for it in range(int(sys.argv[1]) if len(sys.argv) > 1 else 20000):
    hi = random.getrandbits(200)
    L = base + m * hi
    while L % 6 != 1: L += m       # m = 5^8 coprime to 6: adjust high part, keeps the 5-adic low digits
    cons = 0; prev = None
    while L >= 60:
        prev = L; r = L % 5; cons += A[r]; L = (3 * L + C[r]) // 5
    key = (L, prev, cons % 5); cnt[key] = cnt.get(key, 0) + 1
tot = sum(cnt.values())
for k in sorted(cnt): print(k, '%.3f' % (cnt[k] / tot))
