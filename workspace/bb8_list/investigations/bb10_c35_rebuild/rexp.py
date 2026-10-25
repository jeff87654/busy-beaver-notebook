"""End-game dependence on the accumulator residues for 1RB0RA_..._1LI0LC_..._---0LJ_0LD0RA: run the whole machine
(mode A start, b = 6) with every huge post-start accumulator represented by a fixed r-token value RV (r = 3b+1),
for several RV, and report the outcome and the residues of b.  python rexp.py RV1 RV2 ..."""
import sys
import threading
sys.setrecursionlimit(200000)
threading.stack_size(256 * 1024 * 1024 - 4096)
import mf35
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA'


def main():
    for rv in map(int, sys.argv[1:]):
        mf35.FIXREP = rv
        mf35._CACHE.clear()
        k, h = mf35.follow(M, 'A', 3000, 100_000_000)
        zs = [mf35.zeros_of(x) for x in h if x.startswith('J')]
        b = (rv - 1) // 3
        print(f'r={rv} b={b} b%5={b%5} b%7={b%7} b%8={b%8} b%9={b%9} b%11={b%11} -> {k} stages={len(h)} '
              f'last zeros={zs[-3:]} {h[-1]}', flush=True)


t = threading.Thread(target=main)
t.start()
t.join()
