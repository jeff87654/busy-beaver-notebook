"""End-game of 1RB0RA_..._1LI0LC_..._---0LJ_0LD0RA: start the mini-follower at a period-start configuration
[D6^N, D3, D(C), D(2r+3), D3, 0^Z | a=0 | r] with every new accumulator represented by r (FIXREP = r), and report
the outcome (HALT and when, or the number of refills seen).  python endgame.py N Z C1 C2 r1 r2 ..."""
import sys, threading
sys.setrecursionlimit(200000)
threading.stack_size(256 * 1024 * 1024 - 4096)
import mf35
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA'
N, Z, c1, c2 = map(int, sys.argv[1:5])
rs = list(map(int, sys.argv[5:]))
def main():
    for r in rs:
        mf35.FIXREP = r
        mf35._CACHE.clear()
        row = []
        for C in range(c1, c2 + 1):
            toks = [6] * N + [3, C, 2 * r + 3, 3] + [1] * Z + [1, r, 2]
            w = mf35.word_of_tokens(toks)
            k, h = mf35.follow(M, 'A', 60 + 4 * (C // 11 + 3) * 3, 100_000_000, start=(w, len(w), 'G'))
            row.append(f'{C}:{k[0]}{len(h)}')
        b = (r - 1) // 3
        print(f'r={r} (b={b}; mod5 {b%5} mod7 {b%7} mod8 {b%8} mod9 {b%9} mod11 {b%11}) ' + ' '.join(row), flush=True)
t = threading.Thread(target=main); t.start(); t.join()
