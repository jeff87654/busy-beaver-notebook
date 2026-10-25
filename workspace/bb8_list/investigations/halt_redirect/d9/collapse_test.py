"""Literal test of the round-2 'collapse' stage of 1LJ0LH_---1LB:
input  [P..., 9^u, 1, 3, 4, 0, 1, 2, 1^Z | 1 | R]  (post-jump of follower stage 25)
output K-moment structure, for many R (not only residue-class representatives) and several (u, Z)."""
import sys, random
sys.path.insert(0, '.')
import d9f, mf35
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_1LJ0LH_---1LB'
random.seed(1)
def run(P, u, Z, R):
    toks = P + [9]*u + [1, 3, 4, 0, 1, 2] + [1]*Z + [1, R]
    w = mf35.word_of_tokens(toks) + '1010'
    o, um = d9f.stage(M, w, len(w), 'G', 4*10**10)
    f = o.split()
    if f[0] != 'J': return o[:60]
    parts = o.split('|'); t = [int(x) for x in parts[1].split()]
    return d9f.rle(t[2:][::-1]) + f' | a={t[1]} r={t[0]}  far_len={len(parts[2].strip())} steps={f[1]}'
P = [12319, 0, 15165, 1, 4, 15163]
cases = [(2023, 4048), (1015, 2032), (403, 808)]
Rs = [19 + 2520*k for k in (0, 1, 2, 3, 5, 8)] + [7579, 17659] + [random.randrange(100, 20000) for _ in range(6)] + [random.randrange(100, 20000)*3+1 for _ in range(4)]
if __name__ == '__main__':
  for u, Z in cases:
    for R in Rs:
        print(u, Z, R, R % 3, '->', run(P, u, Z, R), flush=True)
