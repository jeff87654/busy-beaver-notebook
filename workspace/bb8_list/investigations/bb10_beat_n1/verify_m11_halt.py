"""Verify that M11 at FIXREP=31 halts at the exact same (4, 0, 2, 0, 1) configuration once max_stages >= 300,
and verify that when C_i < R + 5 (real run where R_15 >> R_13 is false or true), M11 still steps through the exact 5-step prefix chain (3,5)->(1,4)->(4,3)->(2,5)->(0,4)->(4,0,2,0,1)->HALT!"""
import sys, threading
from pathlib import Path

sys.setrecursionlimit(200000)
threading.stack_size(256 * 1024 * 1024 - 4096)

REBUILD_DIR = Path(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb10_c35_rebuild')
sys.path.insert(0, str(REBUILD_DIR))
import mf35
mf35.LOW = 0x08000000 | 0x40

M11 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RI0LC_1RG1LD_1LC0RH_1RG1LF_0LJ0LI_---0RC'

def main():
    for rv in (19, 31, 43):
        mf35.FIXREP = rv
        mf35.REPSEQ = None
        mf35._CACHE.clear()
        k, h = mf35.follow(M11, 'A', 600, 200_000_000)
        print(f"M11 FIXREP={rv}: {k} after {len(h)} stages | last={h[-1]}")

    sv = getattr(mf35._LOCAL, 'sv', None)
    if sv is not None:
        sv.kill()

t = threading.Thread(target=main)
t.start()
t.join()
