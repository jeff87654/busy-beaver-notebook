"""Test the remaining growth_halters.txt candidates ([4/11]..[11/11]) with realistic accumulator sizes (where a jump over a longer 1^Z list produces a larger representative than a jump over a shorter 1^Z list)."""
import sys, threading
from pathlib import Path

sys.setrecursionlimit(200000)
threading.stack_size(256 * 1024 * 1024 - 4096)

REBUILD_DIR = Path(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb10_c35_rebuild')
sys.path.insert(0, str(REBUILD_DIR))
import mf35
mf35.LOW = 0x08000000 | 0x40

def main():
    ms = [l.split()[0] for l in open(REBUILD_DIR / 'growth_halters.txt') if l.strip()]

    # Test 1: [11/11] at stage 11 when r_10 > 2*r_1 (e.g. r_1 = 19 (from 36 zeros), r_10 = 55 or 67 (from 42 zeros))
    m11 = ms[10]
    print("=== Testing [11/11] with r_10 > 2*r_1 at stage 11 ===")
    # In [11/11], stages 0..10 have zeros:
    # st 0: 35 -> r0
    # st 1: 36 -> r1
    # st 2: 36 -> r2
    # st 3: no new param
    # st 4: 41 -> r4
    # st 5: 41 -> r5
    # st 6: 40 -> r6
    # st 7: 40 -> r7
    # st 8: 39 -> r8
    # st 9: 39 -> r9
    # st 10: 42 -> r10
    # So r0 < r1 = r2 < r8 = r9 < r6 = r7 < r4 = r5 < r10!
    seq11 = [19, 31, 31, 67, 67, 55, 55, 43, 43, 91] + [127]*50
    mf35.FIXREP = None
    mf35.REPSEQ = list(seq11)
    mf35._CACHE.clear()
    k, h = mf35.follow(m11, 'A', 60, 200_000_000)
    print(f"[11/11] with size-ordered REPSEQ: result={k} stages={len(h)}")
    for i, x in enumerate(h):
        print(f"  st {i:2d}: {x}")

    # Test 2: [8/11]..[10/11] when r_11 (from 201 zeros) >> 81 (from b=6)
    m8 = ms[7]
    print("\n=== Testing [8/11] with size-ordered REPSEQ ===")
    # In [8/11], stages 0..11 have zeros <= 90, then stage 11 has zeros=201 -> r_11 >> r_0..r_10!
    # Wait: in [8/11], where does 1*83 come from at st 13?
    # Look at st 12 of [8/11]: IN: 1*201 19 2 -> OUT: J step=107174 8 1*199 2
    # Wait: why did st 13 IN have 2 1*83 _*3 2 1*198 19 2?!
    # Let's check what far bits st 12 produced!
    mf35.FIXREP = 19
    mf35.REPSEQ = None
    mf35._CACHE.clear()
    w, hd, st = mf35.xword(6, 35)
    for s in range(15):
        o = mf35.run_stage(m8, w, hd, st, 100_000_000)
        parts = o.split('|')
        print(f"  m8 st {s:2d}: {parts[0].strip()} | far_len={len(parts[2].strip()) if len(parts)>2 else 0}")
        # step mf35 manually:
        break

    # Test [7/11] with size-ordered REPSEQ:
    m7 = ms[6]
    print("\n=== Testing [7/11] with size-ordered REPSEQ ===")
    # In [7/11], st 0..36 have zeros Growing from 36 to 64 every 4 stages:
    # Each 4-stage group (st 1..4, 5..8, ..., 33..36) clears 37, 40, 43, 46, 49, 52, 55, 58, 61 zeros!
    # So the 9 pushed tokens 42_1, 42_2, ..., 42_9 actually have STRICTLY INCREASING sizes R^(1) << R^(2) << ... << R^(9)!
    # Let's assign each stage's representative as a monotone function of the number of zeros cleared!
    sv = getattr(mf35._LOCAL, 'sv', None)
    if sv is not None:
        sv.kill()

t = threading.Thread(target=main)
t.start()
t.join()
