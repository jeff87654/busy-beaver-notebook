"""M3 with ORDERED representatives (the verifier's objection): the accumulators of the real run are not all equal.
Sizes in the real run: b1 (jump 0) ; R0 (after the stage-1 R3 with b-token D2: reset, two units D9->D6->D3) ;
R1 = clear D(2R0+5) ; R2 = clear D(2R1+3) ; R3 = clear D7, D(2R2+6) ; R4 (reset, like R0) ; R5 = clear D(2R4+5).
So R0 ~ R4 << R1 ~ R5 << R2 << R3.  Represent them in that order and follow the whole chain from X(6, 35)."""
import sys, threading
sys.setrecursionlimit(200000)
threading.stack_size(256 * 1024 * 1024 - 4096)
import mf35
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA'
def main():
    for seq in ([91, 19, 31, 55, 91, 19, 31, 55, 91, 19, 31],
                [355, 91, 127, 223, 355, 91, 127, 223, 355, 91, 127],
                [619, 19, 91, 355, 619, 19, 91, 355, 619, 19, 91]):
        mf35.REPSEQ = list(seq); mf35._CACHE.clear()
        k, h = mf35.follow(M, 'A', 40, 2_000_000_000)
        print('reps', seq, '->', k, len(h), flush=True)
        for x in h:
            print('   ', x, flush=True)
t = threading.Thread(target=main); t.start(); t.join()
