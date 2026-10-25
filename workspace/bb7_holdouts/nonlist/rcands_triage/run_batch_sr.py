"""run_batch_sr.py: Complete Prong A + Prong B triage on all 9,055 SR (FR == 0, SRs >= 10) families in rcands_snap.tsv.
Steps:
  1. Run nlp7v.exe 1000000 --life at K in {2, SRK} on all 9,055 SR families -> exact D, DK for all 9,055 families.
  2. Run dlscan2.exe (1000000, 20000) on all 9,055 SR families -> full Prong A digit-list screen across 100% of rcands_snap.tsv.
  3. On all SR families with D >= 4 (plus any dlscan2 hit):
     - nlp7v.exe 2000000 --small at K in {2, DK, SRK, pilot_K} -> SMALL-HALT / Tier-4 classification
     - nlp7_fr_gen.exe 5000000 --htsafe at K in {2, DK, SRK, pilot_K} -> std_HT, max_HT, nolist_halt, intervals
     - nlp7_fr_gen.exe 1000000 (--frgen) at K in {2, DK, SRK, pilot_K} -> FR1, FR2, FR3, FR46, FRref, FRpair
     - dlscan3.exe (2000000, 25000) -> late-blooming / nested digit-list check
Strict rules: creationflags = 0x08000000 | 0x40, W = 2 workers, all files in rcands_triage/.
"""
import collections
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

TRIAGE = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\rcands_triage'
NONLIST = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
NLP7V = os.path.join(NONLIST, 'nlp7v.exe')
NLP7_FRGEN = os.path.join(NONLIST, 'tier4_ht', 'nlp7_fr_gen.exe')
DLSCAN2 = r'C:\Users\jeffr\Downloads\bb8\bb8_list\neighbors\dlscan2.exe'
DLSCAN3 = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\nested_detector\dlscan3.exe'
FLAGS = 0x08000000 | 0x40
W = 2

def main():
    t0 = time.time()
    sr_rows = []
    with open(os.path.join(TRIAGE, 'rcands_snap.tsv'), 'r', encoding='utf-8') as f:
        for l in f:
            if l.startswith(('class', '#')): continue
            parts = l.rstrip('\n').split('\t')
            if len(parts) >= 13 and parts[0] == 'SR':
                sr_rows.append(parts)

    print(f"Loaded {len(sr_rows)} SR families from rcands_snap.tsv", flush=True)
    sub = os.path.join(TRIAGE, 'sr_snap_runs')
    os.makedirs(sub, exist_ok=True)

    # Step 1: --life at K in {2, SRK} on all 9,055 SR families
    life_jobs = collections.defaultdict(list)
    for r in sr_rows:
        m = r[1]
        for k in sorted({'2', r[7]} - {'-', '0'}):
            life_jobs[k].append(m)

    life_tasks = []
    for k, ms in sorted(life_jobs.items()):
        for idx, i in enumerate(range(0, len(ms), 1000)):
            life_tasks.append((k, idx, ms[i:i+1000]))

    def run_life(t):
        k, idx, ms = t
        inp = os.path.join(sub, f'life_K{k}_c{idx:02d}.txt')
        out = os.path.join(sub, f'life_K{k}_c{idx:02d}.tsv')
        if not os.path.exists(out) or os.path.getsize(out) == 0:
            with open(inp, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ms) + '\n')
            cmd = [NLP7V, inp, out, '1000000', '--life', f'--K={k}']
            p = subprocess.Popen(cmd, creationflags=FLAGS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            p.wait()
        return k, out

    print(f"Step 1: Running --life across {len(life_tasks)} chunks for 9,055 SR families...", flush=True)
    with ThreadPoolExecutor(W) as ex:
        life_outs = list(ex.map(run_life, life_tasks))
    print(f"Step 1 (--life) done in {time.time() - t0:.1f}s", flush=True)

    life_map = {}
    life_halt = set()
    for k, out in life_outs:
        for l in open(out, 'r', encoding='utf-8', errors='replace'):
            if l.startswith(('machine', '#')): continue
            f = l.rstrip('\n').split('\t')
            if len(f) >= 6:
                m = f[0]
                if f[5] == 'HALT':
                    life_halt.add(m)
                d = int(f[2]) if float(f[3]) >= 0.5 else 0
                if d > life_map.get(m, (0, '-'))[0]:
                    life_map[m] = (d, k)
                life_map.setdefault(m, (0, k))

    d4_rows = [r for r in sr_rows if life_map.get(r[1], (0, '-'))[0] >= 4]
    d15_rows = [r for r in sr_rows if life_map.get(r[1], (0, '-'))[0] >= 15]
    print(f"SR families with D >= 4: {len(d4_rows)} (of which D >= 15: {len(d15_rows)}, natural life HALT: {len(life_halt)})", flush=True)

    # Step 2: Run dlscan2.exe (1M census, 20k probe) on all 9,055 SR families
    t1 = time.time()
    all_sr_m = [r[1] for r in sr_rows]
    dl2_tasks = []
    for idx, i in enumerate(range(0, len(all_sr_m), 1500)):
        dl2_tasks.append((idx, all_sr_m[i:i+1500]))

    def run_dl2(dt):
        idx, ms = dt
        inp = os.path.join(sub, f'dl2_sr_c{idx:02d}.txt')
        out = os.path.join(sub, f'dl2_sr_c{idx:02d}.tsv')
        if not os.path.exists(out) or os.path.getsize(out) == 0:
            with open(inp, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ms) + '\n')
            cmd = [DLSCAN2, inp, out, '1000000', '20000']
            p = subprocess.Popen(cmd, creationflags=FLAGS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            p.wait()
        return out

    print(f"Step 2: Running dlscan2 on all {len(all_sr_m)} SR families ({len(dl2_tasks)} chunks)...", flush=True)
    with ThreadPoolExecutor(W) as ex:
        dl2_outs = list(ex.map(run_dl2, dl2_tasks))
    print(f"Step 2 (dlscan2) done in {time.time() - t1:.1f}s", flush=True)

    dl2_map = {}
    for out in dl2_outs:
        for l in open(out, 'r', encoding='utf-8', errors='replace'):
            if l.startswith(('machine', '#')): continue
            f = l.rstrip('\n').split('\t')
            if len(f) >= 6:
                dl2_map[f[0]] = f
    print(f"dlscan2 graded hits among 9,055 SR families: {len(dl2_map)}", flush=True)

    # Step 3: On all SR families with D >= 4 (plus any dl2 hit), run --small, --htsafe, --frgen, and dlscan3 (2M, 25k)
    target_set = {r[1] for r in d4_rows} | set(dl2_map.keys())
    target_rows = [r for r in sr_rows if r[1] in target_set]
    print(f"Step 3: Running deep Prong A+B (--small, --htsafe, --frgen, dlscan3) on {len(target_rows)} D>=4 / dl2-hit SR families...", flush=True)

    t2 = time.time()
    deep_jobs_k = collections.defaultdict(list)
    for r in target_rows:
        m = r[1]
        dk = life_map.get(m, (0, '2'))[1]
        ks = sorted({'2', dk, r[7], r[3]} - {'-', '0'})
        for k in ks:
            deep_jobs_k[k].append(m)

    deep_tasks = []
    for k, ms in sorted(deep_jobs_k.items()):
        for idx, i in enumerate(range(0, len(ms), 200)):
            chunk = ms[i:i+200]
            for mode in ['small', 'htsafe', 'frgen']:
                deep_tasks.append((mode, k, idx, chunk))

    def run_deep(t):
        mode, k, idx, ms = t
        inp = os.path.join(sub, f'{mode}_d4_K{k}_c{idx:02d}.txt')
        out = os.path.join(sub, f'{mode}_d4_K{k}_c{idx:02d}.tsv')
        if not os.path.exists(out) or os.path.getsize(out) == 0:
            with open(inp, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ms) + '\n')
            if mode == 'small':
                cmd = [NLP7V, inp, out, '2000000', '--small', f'--K={k}']
            elif mode == 'htsafe':
                cmd = [NLP7_FRGEN, inp, out, '5000000', f'--K={k}', '--htsafe']
            elif mode == 'frgen':
                cmd = [NLP7_FRGEN, inp, out, '1000000', f'--K={k}']
            p = subprocess.Popen(cmd, creationflags=FLAGS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            p.wait()
        return mode, k, out

    with ThreadPoolExecutor(W) as ex:
        deep_outs = list(ex.map(run_deep, deep_tasks))
    print(f"Step 3a (--small, --htsafe, --frgen on D>=4 SR) done in {time.time() - t2:.1f}s", flush=True)

    # Also run dlscan3 (2M census, 25k probe) on target_rows
    t3 = time.time()
    target_ms = [r[1] for r in target_rows]
    dl3_tasks = []
    for idx, i in enumerate(range(0, len(target_ms), 200)):
        dl3_tasks.append((idx, target_ms[i:i+200]))

    def run_dl3(dt):
        idx, ms = dt
        inp = os.path.join(sub, f'dl3_d4_c{idx:02d}.txt')
        out = os.path.join(sub, f'dl3_d4_c{idx:02d}.tsv')
        if not os.path.exists(out) or os.path.getsize(out) == 0:
            with open(inp, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ms) + '\n')
            cmd = [DLSCAN3, inp, out, '2000000', '25000']
            p = subprocess.Popen(cmd, creationflags=FLAGS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            p.wait()
        return out

    with ThreadPoolExecutor(W) as ex:
        dl3_outs = list(ex.map(run_dl3, dl3_tasks))
    print(f"Step 3b (dlscan3 on D>=4 SR) done in {time.time() - t3:.1f}s", flush=True)

    small_map = {}
    ht_map = collections.defaultdict(list)
    frgen_map = collections.defaultdict(list)
    dl3_map = {}

    for mode, k, out in deep_outs:
        for l in open(out, 'r', encoding='utf-8', errors='replace'):
            if l.startswith(('machine', '#')): continue
            f = l.rstrip('\n').split('\t')
            m = f[0]
            if mode == 'small' and len(f) >= 9:
                if f[2] == 'HALT': small_map[m] = 'SMALL-HALT'
                else: small_map.setdefault(m, 'NO-HALT')
            elif mode == 'htsafe' and len(f) >= 8:
                ht_map[m].append((k, f[2], int(f[3]), int(f[4]), int(f[5]), int(f[6]), f[7]))
            elif mode == 'frgen' and len(f) >= 11:
                frgen_map[m].append((k, f[2], int(f[3]), int(f[4]), int(f[5]), int(f[6]), int(f[7]), int(f[8]), int(f[9]), int(f[10])))

    for out in dl3_outs:
        for l in open(out, 'r', encoding='utf-8', errors='replace'):
            if l.startswith(('machine', '#')): continue
            f = l.rstrip('\n').split('\t')
            if len(f) >= 7:
                dl3_map[f[0]] = f

    summary = []
    for r in target_rows:
        m = r[1]
        fam_sz = int(r[2])
        pil_k, nat_lg, maxcnt, srs, srk, srend, srsit_lg, k2_lg, fr, shape = r[3], r[4], r[5], int(r[6]), r[7], r[8], r[9], r[10], int(r[11]), r[12]
        d, dk = life_map.get(m, (0, '-'))
        sm = small_map.get(m, 'NO-HALT')
        tier = 4 if (sm == 'SMALL-HALT' and d >= 4) else 5

        hts = ht_map[m]
        std_ht = max((x[4] for x in hts), default=0)
        max_ht = max((x[5] for x in hts), default=0)
        nolist_halt = 'HALT' if any(x[1] == 'HALT' for x in hts) else 'NO-HALT'
        best_ht_str = '; '.join(f"K{x[0]}:{x[1]}:r={x[2]}:ht={x[4]}/{x[5]}:{x[6]}" for x in hts)

        fgs = frgen_map[m]
        m_fr1 = max((x[4] for x in fgs), default=0)
        m_fr2 = max((x[5] for x in fgs), default=0)
        m_fr3 = max((x[6] for x in fgs), default=0)
        m_fr46 = max((x[7] for x in fgs), default=0)
        m_frref = max((x[8] for x in fgs), default=0)
        m_frpair = max((x[9] for x in fgs), default=0)

        dl = dl3_map.get(m) or dl2_map.get(m)
        dl_grade = dl[3] if dl else '-'
        dl_tmpl = dl[4] if dl else '-'
        dl_extra = (dl[5] + ' | ' + dl[6]) if (dl and len(dl) >= 7) else (dl[5] if dl else '-')

        summary.append((
            tier, -max_ht, -d, m, fam_sz, sm, d, dk, srs, srk, pil_k, nat_lg,
            std_ht, max_ht, nolist_halt, best_ht_str,
            m_fr1, m_fr2, m_fr3, m_fr46, m_frref, m_frpair,
            dl_grade, dl_tmpl, dl_extra, shape
        ))

    summary.sort()
    out_tsv = os.path.join(TRIAGE, 'sr_d4_snap_triage.tsv')
    with open(out_tsv, 'w', encoding='utf-8') as o:
        o.write('tier\tmachine\tfamily_size\tsmall\tD\tDK\tSRs\tSRK\tpilot_K\tnat_lg\tstd_HT\tmax_HT\tnolist_halt\tht_details\tFR1\tFR2\tFR3\tFR46\tFRref\tFRpair\tdl_grade\tdl_tmpl\tdl_details\tshape\n')
        for x in summary:
            o.write('\t'.join(map(str, [x[0]] + list(x[3:]))) + '\n')

    print(f"\n=== SR (D >= 4 or dl2-hit) Triage Summary ({len(summary)} families) ===")
    print(f"  Tier 4 (SMALL-HALT & D>=4): {sum(1 for x in summary if x[0] == 4)}")
    print(f"  Tier 5 (NO-HALT & D>=4 or D<4 dl2-hit): {sum(1 for x in summary if x[0] == 5)}")
    print(f"  std_HT >= 3: {sum(1 for x in summary if x[12] >= 3)}, max_HT >= 3: {sum(1 for x in summary if x[13] >= 3)}")
    print(f"  D >= 15 with FR2 > 0: {sum(1 for x in summary if x[6] >= 15 and x[17] > 0)}")
    print(f"  D >= 15 with FR3 > 0: {sum(1 for x in summary if x[6] >= 15 and x[18] > 0)}")
    print(f"  D >= 15 with FR46 > 0: {sum(1 for x in summary if x[6] >= 15 and x[19] > 0)}")
    print(f"  D >= 15 with FRref > 0: {sum(1 for x in summary if x[6] >= 15 and x[20] > 0)}")
    print(f"  dlscan2/3 graded hits: {sum(1 for x in summary if x[22] != '-')}")
    for x in summary[:25]:
        print(f"  T{x[0]} {x[3]} fam={x[4]} {x[5]} D={x[6]}(K{x[7]}) SRs={x[8]} HT={x[12]}/{x[13]} nolist={x[14]} FR2={x[17]} FRref={x[20]} dl={x[22]} | {x[15][:80]}")

if __name__ == '__main__':
    main()
