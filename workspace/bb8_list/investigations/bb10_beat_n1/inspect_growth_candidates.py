"""Detailed stage-by-stage inspection and ordered-representative (REPSEQ) test of candidates [4/11]..[11/11] from growth_halters.txt."""
import sys, threading
from pathlib import Path

sys.setrecursionlimit(200000)
threading.stack_size(256 * 1024 * 1024 - 4096)

REBUILD_DIR = Path(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb10_c35_rebuild')
sys.path.insert(0, str(REBUILD_DIR))
import mf35
mf35.LOW = 0x08000000 | 0x40

def toks(w):
    t = []; i = 0
    while i < len(w):
        if w[i] == '1':
            j = i; c = 0
            while w[j + 1:j + 3] == '01':
                j += 2; c += 1
            t.append(c); i = j + 1
        else:
            t.append('_'); i += 1
    return t

def trace_machine(name, m, fixrep=19, repseq=None, max_stages=120):
    print("=" * 90)
    print(f"MACHINE {name}: {m} (fixrep={fixrep}, repseq={'yes' if repseq else 'no'})")
    mf35.FIXREP = fixrep
    mf35.REPSEQ = list(repseq) if repseq else None
    mf35._CACHE.clear()
    orig = mf35.run_stage
    st_idx = [0]
    def rs(m_, w, h_, s, mx, maxw=None, rcap=600):
        o = orig(m_, w, h_, s, mx, maxw, rcap)
        in_str = mf35.rle(toks(w))[-120:]
        if o.startswith('J'):
            p = o.split('|'); tt = [int(x) for x in p[1].split()]
            j_str = f"J step={p[0].split()[1]} " + mf35.rle(tt[::-1])[-120:]
        else:
            j_str = o[:100]
        print(f"  st {st_idx[0]:3d} IN : {in_str}")
        print(f"         OUT: {j_str}")
        st_idx[0] += 1
        return o
    mf35.run_stage = rs
    k, h = mf35.follow(m, 'A', max_stages, 200_000_000)
    mf35.run_stage = orig
    print(f"RESULT: {k} after {len(h)} stages | last={h[-1] if h else ''}")
    sys.stdout.flush()

def main():
    ms = [l.split()[0] for l in open(REBUILD_DIR / 'growth_halters.txt') if l.strip()]
    # Inspect [4/11], [6/11], [7/11], [8/11], [11/11]
    for i in [3, 5, 6, 7, 10]:
        trace_machine(f"[{i+1}/11]", ms[i], fixrep=19, max_stages=170)

    sv = getattr(mf35._LOCAL, 'sv', None)
    if sv is not None:
        sv.kill()

t = threading.Thread(target=main)
t.start()
t.join()
