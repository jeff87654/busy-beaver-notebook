"""run_batch_fr_ext.py: Triage the remaining 1,671 FR > 0 families from chunks r0017..r0105 (in rcands_rfull_all.tsv)
so that 100% of all 1,980 FR > 0 families across all 106 completed chunks are triaged!
Runs:
  1. nlp7v.exe 1000000 --life at K in {2, SRK, pilot_K} on all 1,671 extended FR > 0 families -> D, DK
  2. dlscan3.exe (2000000, 25000) on all 1,671 extended FR > 0 families -> late-blooming templated digit-list check
  3. On all extended FR > 0 families with D >= 4 OR FR >= 15 OR SRs >= 15 OR dlscan3 hit:
     - nlp7v.exe 2000000 --small
     - nlp7_fr_gen.exe 5000000 --htsafe
     - nlp7_fr_gen.exe 1000000 (--frgen)
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
    snap_fr = set()
    with open(os.path.join(TRIAGE, 'rcands_snap.tsv'), 'r', encoding='utf-8') as f:
        for l in f:
            if l.startswith(('class', '#')): continue
            p = l.rstrip('\n').split('\t')
            if len(p) >= 13 and p[0] == 'FR':
                snap_fr.add(p[1])

    ext_rows = []
    with open(os.path.join(TRIAGE, 'rcands_rfull_all.tsv'), 'r', encoding='utf-8') as f:
        for l in f:
            if l.startswith(('class', '#')): continue
            p = l.rstrip('\n').split('\t')
            if len(p) >= 13 and p[0] == 'FR' and p[1] not in snap_fr:
                ext_rows.append(p)

    print(f"Loaded {len(ext_rows)} extended FR > 0 families from chunks r0017..r0105", flush=True)
    sub = os.path.join(TRIAGE, 'fr_ext_runs')
    os.makedirs(sub, exist_ok=True)

    # Step 1: --life at K in {2, SRK, pilot_K}
    life_jobs = collections.defaultdict(list)
    for r in ext_rows:
        m = r[1]
        for k in sorted({'2', r[3], r[7]} - {'-', '0'}):
            life_jobs[k].append(m)

    life_tasks = []
    for k, ms in sorted(life_jobs.items()):
        for idx, i in enumerate(range(0, len(ms), 400)):
            life_tasks.append((k, idx, ms[i:i+400]))

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

    with ThreadPoolExecutor(W) as ex:
        life_outs = list(ex.map(run_life, life_tasks))
    print(f"Step 1 (--life on {len(ext_rows)} ext FR) done in {time.time() - t0:.1f}s", flush=True)

    life_map = {}
    for k, out in life_outs:
        for l in open(out, 'r', encoding='utf-8', errors='replace'):
            if l.startswith(('machine', '#')): continue
            f = l.rstrip('\n').split('\t')
            if len(f) >= 6:
                m = f[0]
                d = int(f[2]) if float(f[3]) >= 0.5 else 0
                if d > life_map.get(m, (0, '-'))[0]:
                    life_map[m] = (d, k)
                life_map.setdefault(m, (0, k))

    # Step 2: dlscan3 (2M census, 25k probe) on all 1,671 ext FR families
    t1 = time.time()
    all_ext_m = [r[1] for r in ext_rows]
    dl3_tasks = []
    for idx, i in enumerate(range(0, len(all_ext_m), 300)):
        dl3_tasks.append((idx, all_ext_m[i:i+300]))

    def run_dl3(dt):
        idx, ms = dt
        inp = os.path.join(sub, f'dl3_ext_c{idx:02d}.txt')
        out = os.path.join(sub, f'dl3_ext_c{idx:02d}.tsv')
        if not os.path.exists(out) or os.path.getsize(out) == 0:
            with open(inp, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ms) + '\n')
            cmd = [DLSCAN3, inp, out, '2000000', '25000']
            p = subprocess.Popen(cmd, creationflags=FLAGS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            p.wait()
        return out

    with ThreadPoolExecutor(W) as ex:
        dl3_outs = list(ex.map(run_dl3, dl3_tasks))
    print(f"Step 2 (dlscan3 on {len(all_ext_m)} ext FR) done in {time.time() - t1:.1f}s", flush=True)

    dl3_map = {}
    for out in dl3_outs:
        for l in open(out, 'r', encoding='utf-8', errors='replace'):
            if l.startswith(('machine', '#')): continue
            f = l.rstrip('\n').split('\t')
            if len(f) >= 7:
                dl3_map[f[0]] = f
    print(f"dlscan3 graded hits among 1,671 ext FR families: {len(dl3_map)}", flush=True)

    # Step 3: Deep Prong B (--small, --htsafe, --frgen) on all ext FR with D >= 4 OR FR >= 15 OR SRs >= 15 OR dl3 hit
    deep_rows = [
        r for r in ext_rows
        if life_map.get(r[1], (0, '-'))[0] >= 4 or int(r[11]) >= 15 or int(r[6]) >= 15 or r[1] in dl3_map
    ]
    print(f"Step 3: Running --small, --htsafe, --frgen on {len(deep_rows)} priority ext FR families (including all {sum(1 for r in ext_rows if life_map.get(r[1], (0, '-'))[0] >= 4)} Tier-1 D>=4 families)...", flush=True)

    t2 = time.time()
    deep_jobs_k = collections.defaultdict(list)
    for r in deep_rows:
        m = r[1]
        dk = life_map.get(m, (0, '2'))[1]
        for k in sorted({'2', dk, r[3], r[7]} - {'-', '0'}):
            deep_jobs_k[k].append(m)

    deep_tasks = []
    for k, ms in sorted(deep_jobs_k.items()):
        for idx, i in enumerate(range(0, len(ms), 250)):
            chunk = ms[i:i+250]
            for mode in ['small', 'htsafe', 'frgen']:
                deep_tasks.append((mode, k, idx, chunk))

    def run_deep(t):
        mode, k, idx, ms = t
        inp = os.path.join(sub, f'{mode}_K{k}_c{idx:02d}.txt')
        out = os.path.join(sub, f'{mode}_K{k}_c{idx:02d}.tsv')
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
    print(f"Step 3 done in {time.time() - t2:.1f}s", flush=True)

    small_map = {}
    ht_map = collections.defaultdict(list)
    frgen_map = collections.defaultdict(list)
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

    summary = []
    for r in ext_rows:
        m = r[1]
        fam_sz = int(r[2])
        pil_k, nat_lg, maxcnt, srs, srk, srend, srsit_lg, k2_lg, fr, shape, chunk = r[3], r[4], r[5], int(r[6]), r[7], r[8], r[9], r[10], int(r[11]), r[12], r[13]
        d, dk = life_map.get(m, (0, '-'))
        sm = small_map.get(m, 'NO-HALT' if m in {x[1] for x in deep_rows} else '-')
        tier = 1 if d >= 4 else (2 if sm == 'SMALL-HALT' else 3)

        hts = ht_map[m]
        std_ht = max((x[4] for x in hts), default=0)
        max_ht = max((x[5] for x in hts), default=0)
        nolist_halt = 'HALT' if any(x[1] == 'HALT' for x in hts) else ('NO-HALT' if hts else '-')
        best_ht_str = '; '.join(f"K{x[0]}:{x[1]}:r={x[2]}:ht={x[4]}/{x[5]}:{x[6]}" for x in hts) if hts else '-'

        fgs = frgen_map[m]
        m_fr1 = max((x[4] for x in fgs), default=0)
        m_fr2 = max((x[5] for x in fgs), default=0)
        m_fr3 = max((x[6] for x in fgs), default=0)
        m_fr46 = max((x[7] for x in fgs), default=0)
        m_frref = max((x[8] for x in fgs), default=0)
        m_frpair = max((x[9] for x in fgs), default=0)

        dl = dl3_map.get(m)
        dl_grade = dl[3] if dl else '-'
        dl_tmpl = dl[4] if dl else '-'
        dl_w1 = dl[5] if dl else '-'
        dl_params = dl[6] if dl else '-'

        summary.append((
            tier, -max_ht, -d, -fr, m, fam_sz, chunk, sm, d, dk, fr, srs, srk, pil_k, nat_lg,
            std_ht, max_ht, nolist_halt, best_ht_str,
            m_fr1, m_fr2, m_fr3, m_fr46, m_frref, m_frpair,
            dl_grade, dl_tmpl, dl_w1, dl_params, shape
        ))

    summary.sort()
    out_tsv = os.path.join(TRIAGE, 'fr_ext_triage.tsv')
    with open(out_tsv, 'w', encoding='utf-8') as o:
        o.write('tier\tmachine\tfamily_size\tchunk\tsmall\tD\tDK\tFR\tSRs\tSRK\tpilot_K\tnat_lg\tstd_HT\tmax_HT\tnolist_halt\tht_details\tFR1\tFR2\tFR3\tFR46\tFRref\tFRpair\tdl3_grade\tdl3_tmpl\tdl3_w1\tdl3_params\tshape\n')
        for x in summary:
            o.write('\t'.join(map(str, [x[0]] + list(x[4:]))) + '\n')

    print(f"\n=== Extended FR > 0 Triage Summary (1,671 families in r0017..r0105) ===")
    print(f"  Tier 1 (FR>0 & D>=4): {sum(1 for x in summary if x[0] == 1)}")
    print(f"  dlscan3 graded hits: {sum(1 for x in summary if x[25] != '-')}")
    print(f"  std_HT >= 3: {sum(1 for x in summary if x[15] >= 3)}, max_HT >= 3: {sum(1 for x in summary if x[16] >= 3)}")
    print(f"  std_HT == 2 or max_HT == 2: {sum(1 for x in summary if x[15] == 2 or x[16] == 2)}")
    for x in summary[:25]:
        print(f"  T{x[0]} {x[4]} ({x[6]}) fam={x[5]} {x[7]} D={x[8]}(K{x[9]}) FR={x[10]} SRs={x[11]} HT={x[15]}/{x[16]} nolist={x[17]} dl3={x[25]} | {x[18][:80]}")

if __name__ == '__main__':
    main()
