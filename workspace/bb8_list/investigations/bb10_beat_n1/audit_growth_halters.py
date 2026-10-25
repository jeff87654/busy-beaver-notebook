"""Audit all 11 machines in bb10_c35_rebuild/growth_halters.txt using mf35 (with CREATE_NO_WINDOW | IDLE_PRIORITY_CLASS)
both with fixed representatives (r=19 vs r=31) and with size-ordered representatives (REPSEQ) to see what each of the 11 machines does!"""
import sys, os, threading
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

def main():
    ms = [l.split()[0] for l in open(REBUILD_DIR / 'growth_halters.txt') if l.strip()]
    for idx, m in enumerate(ms):
        print("=" * 80)
        print(f"[{idx+1}/{len(ms)}] {m}  (suffix: {m[42:]})")
        for rv in (19, 31):
            mf35.FIXREP = rv
            mf35.REPSEQ = None
            mf35._CACHE.clear()
            k, h = mf35.follow(m, 'A', 250, 100_000_000)
            zs = [z for z in (mf35.zeros_of(x) for x in h if x.startswith('J')) if z is not None]
            print(f"  FIXREP={rv:2d}: {k:9s} stages={len(h):3d} last={h[-1]} zeros[:14]={zs[:14]} zeros[-6:]={zs[-6:]}")
        # Also print first 10 stage configurations at FIXREP=19
        mf35.FIXREP = 19
        mf35.REPSEQ = None
        mf35._CACHE.clear()
        orig = mf35.run_stage
        trace_lines = []
        def rs(m_, w, h_, s, mx, maxw=None, rcap=600):
            o = orig(m_, w, h_, s, mx, maxw, rcap)
            if len(trace_lines) < 12:
                in_str = mf35.rle(toks(w))[-110:]
                if o.startswith('J'):
                    p = o.split('|'); tt = [int(x) for x in p[1].split()]
                    j_str = f"J step={p[0].split()[1]} " + mf35.rle(tt[::-1])[-110:]
                else:
                    j_str = o[:100]
                trace_lines.append((in_str, j_str))
            return o
        mf35.run_stage = rs
        mf35.follow(m, 'A', 12, 100_000_000)
        mf35.run_stage = orig
        for st_i, (in_s, j_s) in enumerate(trace_lines):
            print(f"    st {st_i:2d} IN: {in_s}")
            print(f"          OUT: {j_s}")
        sys.stdout.flush()
    sv = getattr(mf35._LOCAL, 'sv', None)
    if sv is not None:
        sv.kill()

t = threading.Thread(target=main)
t.start()
t.join()
