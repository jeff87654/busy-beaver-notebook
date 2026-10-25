"""run_batch_fr.py: Complete Prong A + Prong B triage on all 309 FR > 0 families in rcands_snap.tsv.
Runs:
  1. nlp7v.exe 1000000 --life at K in {2, SRK, pilot_K} -> D, DK
  2. nlp7v.exe 2000000 --small at K in {2, SRK, pilot_K} -> SMALL-HALT / NO-HALT
  3. nlp7_fr_gen.exe 5000000 --htsafe at K in {2, SRK, pilot_K} -> std_HT, max_HT, forced intervals, nolist_halt
  4. nlp7_fr_gen.exe 1000000 (--frgen) at K in {2, SRK, pilot_K} -> FR1, FR2, FR3, FR46, FRref, FRpair
  5. dlscan3.exe (CENSUS=3000000, N=30000, --all) -> late-blooming templated digit-list check
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
DLSCAN3 = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\nested_detector\dlscan3.exe'
FLAGS = 0x08000000 | 0x40
W = 2

def main():
    t0 = time.time()
    fr_rows = []
    with open(os.path.join(TRIAGE, 'rcands_snap.tsv'), 'r', encoding='utf-8') as f:
        for l in f:
            if l.startswith(('class', '#')): continue
            parts = l.rstrip('\n').split('\t')
            if len(parts) >= 13 and parts[0] == 'FR':
                fr_rows.append(parts)

    print(f"Loaded {len(fr_rows)} FR > 0 families from rcands_snap.tsv", flush=True)
    # Columns of rcands_snap.tsv:
    # 0:class, 1:machine, 2:family_size, 3:K, 4:nat_lg, 5:maxcnt, 6:SRs, 7:SRK, 8:SRend, 9:SRsit_lg, 10:k2_lg, 11:FR, 12:shape
    jobs_by_k = collections.defaultdict(list)
    for r in fr_rows:
        m = r[1]
        ks = sorted({'2', r[3], r[7]} - {'-', '0'})
        for k in ks:
            jobs_by_k[k].append(m)

    sub = os.path.join(TRIAGE, 'fr_snap_runs')
    os.makedirs(sub, exist_ok=True)

    tasks = []
    for k, ms in sorted(jobs_by_k.items()):
        # Split into chunks of 160 so W=2 workers run in parallel even within K=2
        for idx, i in enumerate(range(0, len(ms), 160)):
            chunk = ms[i:i+160]
            for mode in ['life', 'small', 'htsafe', 'frgen']:
                tasks.append((mode, k, idx, chunk))

    def run_task(t):
        mode, k, idx, ms = t
        inp = os.path.join(sub, f'{mode}_K{k}_c{idx:02d}.txt')
        out = os.path.join(sub, f'{mode}_K{k}_c{idx:02d}.tsv')
        if not os.path.exists(out) or os.path.getsize(out) == 0:
            with open(inp, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ms) + '\n')
            if mode == 'life':
                cmd = [NLP7V, inp, out, '1000000', '--life', f'--K={k}']
            elif mode == 'small':
                cmd = [NLP7V, inp, out, '2000000', '--small', f'--K={k}']
            elif mode == 'htsafe':
                cmd = [NLP7_FRGEN, inp, out, '5000000', f'--K={k}', '--htsafe']
            elif mode == 'frgen':
                cmd = [NLP7_FRGEN, inp, out, '1000000', f'--K={k}']
            p = subprocess.Popen(cmd, creationflags=FLAGS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            p.wait()
        return mode, k, out

    print(f"Running {len(tasks)} Prong-B task chunks across W={W} workers...", flush=True)
    with ThreadPoolExecutor(W) as ex:
        done_tasks = list(ex.map(run_task, tasks))
    print(f"Prong-B tasks finished in {time.time() - t0:.1f}s", flush=True)

    # Now run dlscan3.exe (CENSUS=3000000, N=30000, --all) in 2 chunks on W=2 workers
    all_fr_machines = [r[1] for r in fr_rows]
    dl_tasks = []
    mid = (len(all_fr_machines) + 1) // 2
    for idx, chunk in enumerate([all_fr_machines[:mid], all_fr_machines[mid:]]):
        dl_tasks.append((idx, chunk))

    def run_dl3(dt):
        idx, ms = dt
        inp = os.path.join(sub, f'dl3_fr_c{idx:02d}.txt')
        out = os.path.join(sub, f'dl3_fr_c{idx:02d}.tsv')
        if not os.path.exists(out) or os.path.getsize(out) == 0:
            with open(inp, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ms) + '\n')
            cmd = [DLSCAN3, inp, out, '3000000', '30000', '--all']
            p = subprocess.Popen(cmd, creationflags=FLAGS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            p.wait()
        return out

    t1 = time.time()
    print(f"Running dlscan3 (3M census, 30k probe, --all) on {len(all_fr_machines)} FR families...", flush=True)
    with ThreadPoolExecutor(W) as ex:
        dl_outs = list(ex.map(run_dl3, dl_tasks))
    print(f"dlscan3 finished in {time.time() - t1:.1f}s", flush=True)

    # Aggregate results
    life_map = {}
    small_map = {}
    ht_map = collections.defaultdict(list)
    frgen_map = collections.defaultdict(list)
    dl3_map = {}

    for mode, k, out in done_tasks:
        for l in open(out, 'r', encoding='utf-8', errors='replace'):
            if l.startswith(('machine', '#')): continue
            f = l.rstrip('\n').split('\t')
            m = f[0]
            if mode == 'life' and len(f) >= 6:
                d = int(f[2]) if float(f[3]) >= 0.5 else 0
                if d > life_map.get(m, (0, '-'))[0]:
                    life_map[m] = (d, k)
                life_map.setdefault(m, (0, k))
            elif mode == 'small' and len(f) >= 9:
                if f[2] == 'HALT':
                    small_map[m] = 'SMALL-HALT'
                else:
                    small_map.setdefault(m, 'NO-HALT')
            elif mode == 'htsafe' and len(f) >= 8:
                # m, K, st, rounds, lv, std_ht, max_ht, ivs
                ht_map[m].append((k, f[2], int(f[3]), int(f[4]), int(f[5]), int(f[6]), f[7]))
            elif mode == 'frgen' and len(f) >= 11:
                # m, K, st, srl, srs, fr1, fr2, fr3, fr46, frref, frpair
                frgen_map[m].append((k, f[2], int(f[3]), int(f[4]), int(f[5]), int(f[6]), int(f[7]), int(f[8]), int(f[9]), int(f[10])))

    for out in dl_outs:
        for l in open(out, 'r', encoding='utf-8', errors='replace'):
            if l.startswith(('machine', '#')): continue
            f = l.rstrip('\n').split('\t')
            if len(f) >= 7:
                dl3_map[f[0]] = f

    # Write combined summary table for all 309 FR families
    summary_rows = []
    for r in fr_rows:
        m = r[1]
        fam_sz = int(r[2])
        pil_k, nat_lg, maxcnt, srs, srk, srend, srsit_lg, k2_lg, fr, shape = r[3], r[4], r[5], int(r[6]), r[7], r[8], r[9], r[10], int(r[11]), r[12]
        d, dk = life_map.get(m, (0, '-'))
        sm = small_map.get(m, 'NO-HALT')
        tier = 1 if d >= 4 else (2 if sm == 'SMALL-HALT' else 3)

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

        dl = dl3_map.get(m, [m, '-1', '0', '-', '-', '-', '-', '-'])
        dl_ntmpl = int(dl[2])
        dl_grade = dl[3]
        dl_tmpl = dl[4]
        dl_w1 = dl[5]
        dl_params = dl[6]

        summary_rows.append((
            tier, -d, -max_ht, -fr, m, fam_sz, sm, d, dk, fr, srs, srk, pil_k, nat_lg,
            std_ht, max_ht, nolist_halt, best_ht_str,
            m_fr1, m_fr2, m_fr3, m_fr46, m_frref, m_frpair,
            dl_ntmpl, dl_grade, dl_tmpl, dl_w1, dl_params, shape
        ))

    summary_rows.sort()
    out_tsv = os.path.join(TRIAGE, 'fr_snap_triage.tsv')
    with open(out_tsv, 'w', encoding='utf-8') as o:
        o.write('tier\tmachine\tfamily_size\tsmall\tD\tDK\tFR\tSRs\tSRK\tpilot_K\tnat_lg\tstd_HT\tmax_HT\tnolist_halt\tht_details\tFR1\tFR2\tFR3\tFR46\tFRref\tFRpair\tdl3_ntmpl\tdl3_grade\tdl3_tmpl\tdl3_w1\tdl3_params\tshape\n')
        for x in summary_rows:
            o.write('\t'.join(map(str, [x[0]] + list(x[4:]))) + '\n')

    tiers = collections.Counter(x[0] for x in summary_rows)
    dl_grades = collections.Counter(x[25] for x in summary_rows)
    print(f"\n=== FR > 0 Triage Summary (309 families in rcands_snap.tsv) ===")
    print(f"  Tiers: {dict(sorted(tiers.items()))} (Tier 1 = FR>0 & D>=4; Tier 2 = FR>0 & D<4 & SMALL-HALT; Tier 3 = other FR>0)")
    print(f"  dlscan3 grades: {dict(dl_grades)}")
    print(f"  dlscan3 n_templates > 0: {sum(1 for x in summary_rows if x[24] > 0)}")
    print(f"  std_HT >= 3: {sum(1 for x in summary_rows if x[14] >= 3)}, max_HT >= 3: {sum(1 for x in summary_rows if x[15] >= 3)}")
    print(f"  FR2 > 0: {sum(1 for x in summary_rows if x[19] > 0)}, FR3 > 0: {sum(1 for x in summary_rows if x[20] > 0)}, FR46 > 0: {sum(1 for x in summary_rows if x[21] > 0)}, FRref > 0: {sum(1 for x in summary_rows if x[22] > 0)}")
    print("\nTop 30 Tier-1 (FR > 0 & D >= 4) candidates:")
    t1_rows = [x for x in summary_rows if x[0] == 1]
    for x in t1_rows[:30]:
        print(f"  {x[4]} fam={x[5]} {x[6]} D={x[7]}(K{x[8]}) FR={x[9]} SRs={x[10]} HT={x[14]}/{x[15]} nolist={x[16]} dl3={x[25]}(nt={x[24]}) | {x[17][:80]}")

if __name__ == '__main__':
    main()
