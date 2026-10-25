"""Audit all 151 unscreened HALT-after-full-cycle leaves and all MAXSTAGES-after-full-cycle leaves
with a reachable halt slot in bb10_c35_rebuild (mf_rest.tsv, mf_all.tsv, sib_j.tsv, ola_j.tsv)."""
import os, re, sys, threading
sys.setrecursionlimit(200000)
threading.stack_size(256 * 1024 * 1024 - 4096)

C35_DIR = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb10_c35_rebuild'
OUT_DIR = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb10_deep_fgh_and_bb9_bouncer'
sys.path.insert(0, C35_DIR)
import mf35, mf35g

# Enforce CREATE_NO_WINDOW | IDLE_PRIORITY_CLASS (0x08000000 | 0x40) on all stage35/stage35g servers
mf35.LOW = 0x08000000 | 0x40
mf35g.LOW = 0x08000000 | 0x40

def has_reachable_halt(m):
    parts = m.split('_')
    # States I (index 8) and J (index 9)
    i_row, j_row = parts[8], parts[9]
    i0, i1 = i_row[:3], i_row[3:]
    j0, j1 = j_row[:3], j_row[3:]
    # Does I have a halt slot?
    if i0 == '---' or i1 == '---':
        return True
    # Otherwise, J is only reachable if i0 or i1 transitions to J
    if i0[2] == 'J' or i1[2] == 'J':
        if j0 == '---' or j1 == '---':
            return True
    return False

def get_zeros(hist_list):
    return [mf35.zeros_of(x) for x in hist_list if x.startswith('J')]

def main():
    out_path = os.path.join(OUT_DIR, 'c35_rebuild_audit_out.txt')
    fo = open(out_path, 'w')
    def log(s):
        print(s, flush=True)
        fo.write(s + '\n')
        fo.flush()

    levels2 = {}
    for l in open(os.path.join(C35_DIR, 'levels2.tsv')):
        if '\t' in l:
            f = l.rstrip('\n').split('\t')
            levels2[f[0]] = f

    unscreened_halts = []
    maxstages_big = []
    for l in open(os.path.join(C35_DIR, 'mf_rest.tsv')):
        f = l.rstrip('\n').split('\t')
        if len(f) < 5: continue
        m, kind, stg, big, hist_str = f[0], f[1], int(f[2]), int(f[3]), f[4]
        hist_a = hist_str.split(' ; ')
        if kind == 'HALT' and big >= 1 and m not in levels2:
            unscreened_halts.append((m, stg, big, hist_a))
        elif kind == 'MAXSTAGES' and big >= 1:
            maxstages_big.append((m, stg, big, hist_a))

    log(f"=== SECTION 1: Auditing {len(unscreened_halts)} Unscreened HALT-After-Full-Cycle Machines in mf_rest.tsv ===")
    dep_halts = []
    same_cnt = 0
    depearly_cnt = 0
    for idx, (m, stg, big, hist_a) in enumerate(unscreened_halts):
        za = get_zeros(hist_a)
        mf35.FIXREP = None; mf35.REPSEQ = None
        k_f, hist_f = mf35.follow(m, 'F', 300, 100_000_000)
        zf = get_zeros(hist_f)
        first_big = next((i for i, z in enumerate(za) if z is not None and z >= 50), None)
        diff = next((i for i, (x, y) in enumerate(zip(za, zf)) if x != y), None)
        if diff is None and len(za) != len(zf):
            diff = min(len(za), len(zf))
        tag = 'same'
        if diff is not None:
            tag = 'DEP' if first_big is not None and diff > first_big else 'dep-early'
        if tag == 'same':
            same_cnt += 1
        elif tag == 'dep-early':
            depearly_cnt += 1
        else:
            dep_halts.append((m, k_f, len(hist_f), first_big, diff, za, zf, hist_a, hist_f))
            log(f"  [DEP-HALT {len(dep_halts)}] {m[49:]} A:HALT({len(hist_a)}) F:{k_f}({len(hist_f)}) first_big={first_big} diff={diff} za={za[:10]} zf={zf[:10]}")

    log(f"Summary of 151 unscreened HALT machines: same={same_cnt}, dep-early={depearly_cnt}, DEP={len(dep_halts)}")

    if dep_halts:
        log("\n--- Testing DEP-HALT machines with FIXREP=(19 vs 31) and ordered REPSEQ ---")
        for m, k_f, len_f, first_big, diff, za, zf, hist_a, hist_f in dep_halts:
            res_fix = []
            for rv in (19, 31):
                mf35.FIXREP = rv; mf35.REPSEQ = None; mf35._CACHE.clear()
                k_r, h_r = mf35.follow(m, 'A', 300, 100_000_000)
                zr = [z for z in get_zeros(h_r) if z is not None]
                res_fix.append((rv, k_r, len(h_r), zr[:12], zr[-6:], h_r[-1]))
            mf35.FIXREP = None
            mf35.REPSEQ = [91, 19, 31, 55, 91, 19, 31, 55, 91, 19, 31, 55, 91, 127, 223, 355] * 20
            mf35._CACHE.clear()
            k_o, h_o = mf35.follow(m, 'A', 300, 100_000_000)
            zo = [z for z in get_zeros(h_o) if z is not None]
            mf35.REPSEQ = None
            log(f"  {m[49:]}:")
            for rv, k_r, l_r, z1, z2, last in res_fix:
                log(f"    FIXREP={rv}: {k_r} stg={l_r} zs_start={z1} zs_end={z2} last={last}")
            log(f"    ORDERED  : {k_o} stg={len(h_o)} zs_start={zo[:12]} zs_end={zo[-6:]} last={h_o[-1]}")

    # Section 2: Audit all 396 MAXSTAGES with big >= 1 in mf_rest.tsv
    reach_ms = [(m, stg, big, hist_a) for (m, stg, big, hist_a) in maxstages_big if has_reachable_halt(m)]
    unreach_ms = len(maxstages_big) - len(reach_ms)
    log(f"\n=== SECTION 2: Auditing {len(maxstages_big)} MAXSTAGES (big>=1) in mf_rest.tsv (reachable_halt={len(reach_ms)}, no_reachable_halt={unreach_ms}) ===")

    ms_halts_in_F_or_ord = []
    ms_dep = []
    ms_same = 0
    ms_depearly = 0
    for m, stg, big, hist_a in reach_ms:
        za = get_zeros(hist_a)
        mf35.FIXREP = None; mf35.REPSEQ = None
        k_f, hist_f = mf35.follow(m, 'F', 300, 50_000_000)
        zf = get_zeros(hist_f)
        first_big = next((i for i, z in enumerate(za) if z is not None and z >= 50), None)
        diff = next((i for i, (x, y) in enumerate(zip(za, zf)) if x != y), None)
        if diff is None and len(za) != len(zf):
            diff = min(len(za), len(zf))
        tag = 'same'
        if diff is not None:
            tag = 'DEP' if first_big is not None and diff > first_big else 'dep-early'
        if tag == 'same':
            ms_same += 1
        elif tag == 'dep-early':
            ms_depearly += 1
        else:
            ms_dep.append((m, k_f, len(hist_f), first_big, diff, za, zf, hist_a, hist_f))
        if k_f == 'HALT':
            ms_halts_in_F_or_ord.append((m, 'F', len(hist_f), hist_f[-1], za[:10], zf[:10]))

    log(f"MAXSTAGES (reachable_halt={len(reach_ms)}) mode-F screen: same={ms_same}, dep-early={ms_depearly}, DEP={len(ms_dep)}, HALT_in_F={len(ms_halts_in_F_or_ord)}")
    for m, k_f, l_f, fb, df, za, zf, ha, hf in ms_dep[:30]:
        log(f"  [MS-DEP] {m[49:]} F:{k_f}({l_f}) fb={fb} diff={df} za_s={za[:6]} za_e={za[-4:]} zf_s={zf[:6]} zf_e={zf[-4:]}")

    # Test all ms_dep with ordered representatives REPSEQ to see if any halts when R_old != R_new!
    log(f"\n--- Testing all {len(ms_dep)} MS-DEP machines with Ordered Representatives (REPSEQ) ---")
    ord_halts = []
    for m, k_f, l_f, fb, df, za, zf, ha, hf in ms_dep:
        mf35.FIXREP = None
        mf35.REPSEQ = [91, 19, 31, 55, 91, 19, 31, 55, 91, 19, 31, 55, 91, 127, 223, 355] * 25
        mf35._CACHE.clear()
        k_o, h_o = mf35.follow(m, 'A', 300, 50_000_000)
        mf35.REPSEQ = None
        if k_o == 'HALT':
            zo = [z for z in get_zeros(h_o) if z is not None]
            ord_halts.append((m, len(h_o), h_o[-1], zo))
            log(f"  [ORD-HALT] {m[49:]} -> HALT at stage {len(h_o)} ({h_o[-1]}) zs={zo[:12]}..{zo[-6:]}")
    log(f"Total MS-DEP machines halting under ORDERED reps: {len(ord_halts)}")

    # Section 3: Audit the 42 MAXSTAGES machines in sib_j.tsv
    log(f"\n=== SECTION 3: Auditing the 42 MAXSTAGES Machines in sib_j.tsv ===")
    sib_ms = []
    for l in open(os.path.join(C35_DIR, 'sib_j.tsv')):
        f = l.rstrip('\n').split('\t')
        if len(f) >= 2 and f[1] == 'MAXSTAGES':
            sib_ms.append(f[0])
    for m in sib_ms:
        mf35g._CACHE.clear()
        k18, h18 = mf35g.follow('SIB', m, stages=120, maxs=20_000_000, b0=6, fixrep=18)
        mf35g._CACHE.clear()
        k30, h30 = mf35g.follow('SIB', m, stages=120, maxs=20_000_000, b0=6, fixrep=30)
        z18 = [z for z in get_zeros(h18) if z is not None]
        z30 = [z for z in get_zeros(h30) if z is not None]
        # Check if z18[3:] != z30[3:] (since first 4 jumps are base SIB's 67, 67, 108, 108)
        diff_post = (z18[4:] != z30[4:])
        if diff_post or k18 == 'HALT' or k30 == 'HALT':
            log(f"  [SIB-MS-DIFF] {m[49:]} r18:{k18}({len(h18)}) r30:{k30}({len(h30)}) z18={z18[:12]} z30={z30[:12]}")
        else:
            log(f"  [SIB-MS-SAME] {m[49:]} z18==z30 (periodicity): {z18[:12]}..{z18[-4:]}")

    fo.close()

t = threading.Thread(target=main)
t.start()
t.join()
