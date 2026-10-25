"""Counter-exhaustion experiment for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA:
start the mini-follower (mode A) from a period-start K-moment of its run, [D6^N, D3, D(C), D44, 0^Z | 0 | b-token D2],
with the counter token C varied, and report the outcome.  python cexp.py N Z C1 C2"""
import sys, mf35
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA'
N, Z, c1, c2 = map(int, sys.argv[1:5])
for C in range(c1, c2 + 1):
    toks = [6] * N + [3, C, 44] + [1] * Z + [1, 2, 2]
    w = mf35.word_of_tokens(toks)
    k, h = mf35.follow(M, 'A', 400, 50_000_000, start=(w, len(w), 'G'))
    zs = [mf35.zeros_of(x) for x in h if x.startswith('J')]
    print(C, C % 11, k, len(h), zs[:3], '...', zs[-4:], h[-1], flush=True)
