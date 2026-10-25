"""Whole-chain run of M3 in the representative world: stage 0 from X(6, 35), every literal stage simulated literally,
every jump abstract (follow2.jump), every post-start accumulator represented by r = FIXREP.  Prints a compact trace of
the counter token and the zero-run length per stage and the outcome.  python m3chain.py FIXREP [MAXSTAGES]"""
import sys, threading
sys.setrecursionlimit(200000)
threading.stack_size(256 * 1024 * 1024 - 4096)
import mf35
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA'
rv = int(sys.argv[1]); ms = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
def main():
    mf35.FIXREP = rv
    k, h = mf35.follow(M, 'A', ms, 2_000_000_000)
    zs = [mf35.zeros_of(x) for x in h if x.startswith('J')]
    print('FIXREP', rv, 'result', k, 'stages', len(h), 'last', h[-1])
    print('zeros per jump (every 4th):', zs[::4][:60], '...', zs[-8:])
t = threading.Thread(target=main); t.start(); t.join()
