"""run_ht.py: Run nlp7v.exe 5000000 --small --nolist on:
  Phase 1: All 932 Tier-4 rows (small == SMALL-HALT, D >= 4, FR == 0), ordered by D descending.
  Phase 2: All Tier-5 and Tier-2 SMALL-HALT rows (3,224 rows), reusing exact (HALT & listcut==0) runs from post/small_K*.tsv
           and running nlp7v.exe 5000000 --small --nolist on all remaining (machine, K) pairs.
Strict rules:
  - Uses Idle priority (creationflags=0x40) and at most W=2 concurrent workers.
  - Writes only inside tier4_ht/. Does NOT touch final.tsv, cands.tsv, pids.txt, or post/.
"""
import collections
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
NONLIST = os.path.dirname(HERE)
EXE = os.path.join(NONLIST, 'nlp7v.exe')
PIDS_LOG = os.path.join(HERE, 'pids_tier4.txt')
W = int(sys.argv[1]) if len(sys.argv) > 1 else 2
PHASE = sys.argv[2] if len(sys.argv) > 2 else 'all'
CHUNK_SIZE = 250
_lock = threading.Lock()


def load_data():
    cands = {}
    with open(os.path.join(NONLIST, 'cands.tsv')) as f:
        for l in f:
            if l.startswith('class'):
                continue
            r = l.rstrip('\n').split('\t')
            cands[r[1]] = r
    final_rows = []
    with open(os.path.join(NONLIST, 'final.tsv')) as f:
        for l in f:
            if l.startswith('tier'):
                continue
            final_rows.append(l.rstrip('\n').split('\t'))
    small_existing = {}
    for k in ['2', '3', '4', '5', '6']:
        p = os.path.join(NONLIST, 'post', f'small_K{k}.tsv')
        if os.path.exists(p):
            with open(p) as f:
                for l in f:
                    parts = l.rstrip('\n').split('\t')
                    if len(parts) >= 9:
                        small_existing[(parts[0], k)] = parts
    return cands, final_rows, small_existing


def run_chunk(args):
    tag, k, idx, machines, out_tsv = args
    inp_txt = os.path.join(HERE, f'{tag}_K{k}_c{idx:02d}.txt')
    part_tsv = os.path.join(HERE, f'{tag}_K{k}_c{idx:02d}.part.tsv')
    done_tsv = os.path.join(HERE, f'{tag}_K{k}_c{idx:02d}.tsv')
    if os.path.exists(done_tsv):
        existing = [l for l in open(done_tsv) if not l.startswith(('machine', '#'))]
        if len(existing) == len(machines):
            return done_tsv
    with open(inp_txt, 'w') as f:
        f.write('\n'.join(machines) + '\n')
    t0 = time.time()
    p = subprocess.Popen(
        [EXE, inp_txt, part_tsv, '5000000', '--small', '--nolist', f'--K={k}'],
        creationflags=0x40,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    with _lock, open(PIDS_LOG, 'a') as pf:
        pf.write(f'{p.pid}\t{time.strftime("%Y-%m-%d %H:%M:%S")}\tnlp7v.exe {tag} K{k} c{idx:02d} ({len(machines)}m)\n')
    p.wait()
    dt = time.time() - t0
    with open(done_tsv, 'w') as o:
        if os.path.exists(part_tsv):
            for l in open(part_tsv):
                if not l.startswith(('machine', '#')):
                    o.write(l)
            os.remove(part_tsv)
    print(f'[{tag}] K={k} chunk {idx:02d} ({len(machines)} machines) done in {dt:.1f}s', flush=True)
    return done_tsv


def execute_jobs(tag, jobs_by_k):
    tasks = []
    for k in sorted(jobs_by_k):
        ms = jobs_by_k[k]
        for idx, i in enumerate(range(0, len(ms), CHUNK_SIZE)):
            chunk = ms[i:i + CHUNK_SIZE]
            tasks.append((tag, k, idx, chunk, os.path.join(HERE, f'{tag}_K{k}.tsv')))
    with ThreadPoolExecutor(W) as ex:
        chunk_files = list(ex.map(run_chunk, tasks))
    # Merge per K
    results = {}
    for k in sorted(jobs_by_k):
        merged_path = os.path.join(HERE, f'{tag}_K{k}.tsv')
        with open(merged_path, 'w') as o:
            for t, ck, idx, _, _ in tasks:
                if ck != k:
                    continue
                cf = os.path.join(HERE, f'{t}_K{ck}_c{idx:02d}.tsv')
                if os.path.exists(cf):
                    for l in open(cf):
                        o.write(l)
                        parts = l.rstrip('\n').split('\t')
                        if len(parts) >= 9:
                            results[(parts[0], k)] = parts
    return results


def summarize_rows(label, rows, cands, results_map, out_file):
    # Columns of results_map[(m, k)]:
    # [0]=machine, [1]=K, [2]=status(HALT/LOOP/-), [3]=listcut, [4]=rounds, [5]=levels, [6]=log10steps, [7]=ht, [8]=ivs
    summary = []
    for r in rows:
        # final.tsv columns:
        # 0:tier, 1:class, 2:small, 3:machine, 4:family, 5:D, 6:DK, 7:FR, 8:HT, 9:HTiv, 10:SRs, 11:K, 12:nat_lg, 13:shape
        m = r[3]
        c = cands[m]
        ks = sorted({'2', r[6], c[7], c[3]} - {'-'})
        best_ht = -1
        best_ht_str = '-'
        best_rounds = 0
        best_levels = 0
        any_halt = False
        all_k_info = []
        for k in ks:
            res = results_map.get((m, k))
            if not res:
                continue
            st, lc, rds, lvs, lgs, ht_val, ivs = res[2], int(res[3]), int(res[4]), int(res[5]), float(res[6]), int(res[7]), res[8]
            if st == 'HALT':
                any_halt = True
            if rds > best_rounds:
                best_rounds = rds
            if lvs > best_levels:
                best_levels = lvs
            ht_tag = f'K{k}:{ivs}' + (' HALT' if st == 'HALT' else '')
            all_k_info.append(f'K{k}:{st}:r={rds}:lv={lvs}:ht={ht_val}:{ivs}')
            if ht_val > best_ht or (ht_val == best_ht and st == 'HALT' and 'HALT' not in best_ht_str):
                best_ht = ht_val
                best_ht_str = ht_tag
        summary.append((
            r[0], r[1], r[2], m, int(r[4]), int(r[5]), r[6], int(r[7]),
            best_ht, best_ht_str, 'HALT' if any_halt else 'NO-HALT',
            best_rounds, best_levels, int(r[10]), r[11], r[12], '; '.join(all_k_info), r[13]
        ))
    # Sort by best_ht desc, D desc, best_rounds desc
    summary.sort(key=lambda x: (-x[8], -x[5], -x[11]))
    with open(out_file, 'w') as o:
        o.write('tier\tclass\tsmall\tmachine\tfamily\tD\tDK\tFR\tHT\tHTiv\tnolist_halt\tmax_rounds\tmax_levels\tSRs\tK\tnat_lg\tall_K_details\tshape\n')
        for x in summary:
            o.write('\t'.join(map(str, x)) + '\n')
    ht_dist = collections.Counter(x[8] for x in summary)
    halt_dist = collections.Counter(x[10] for x in summary)
    print(f'=== {label} ({len(summary)} rows) ===')
    print('HT distribution:', sorted(ht_dist.items()))
    print('nolist_halt distribution:', dict(halt_dist))
    print('Top 25 rows by (HT, D, max_rounds):')
    for x in summary[:25]:
        print(f'  T{x[0]} {x[3]} fam={x[4]} D={x[5]}(K{x[6]}) SRs={x[13]} HT={x[8]} [{x[9]}] nolist={x[10]} max_r={x[11]} max_lv={x[12]}')
    return summary


def main():
    cands, final_rows, small_existing = load_data()

    # Phase 1: Tier 4 (all 932 rows, ordered by D descending as in final.tsv)
    t4_rows = [r for r in final_rows if r[0] == '4']
    t4_jobs = collections.defaultdict(list)
    for r in t4_rows:
        m = r[3]
        c = cands[m]
        for k in sorted({'2', r[6], c[7], c[3]} - {'-'}):
            t4_jobs[k].append(m)

    if PHASE in ('1', 'all'):
        print(f'Starting Phase 1: {len(t4_rows)} Tier-4 rows, {sum(len(v) for v in t4_jobs.values())} (machine, K) runs...', flush=True)
        t4_res = execute_jobs('t4_ht', t4_jobs)
        summarize_rows('Phase 1: Tier-4 (D >= 4, FR = 0, SMALL-HALT)', t4_rows, cands, t4_res, os.path.join(HERE, 'tier4_results.tsv'))

    if PHASE in ('2', 'all'):
        t52_rows = [r for r in final_rows if r[2] == 'SMALL-HALT' and r[0] in ('2', '5')]
        t52_jobs = collections.defaultdict(list)
        t52_res = {}
        reused = 0
        for r in t52_rows:
            m = r[3]
            c = cands[m]
            for k in sorted({'2', r[6], c[7], c[3]} - {'-'}):
                ex = small_existing.get((m, k))
                if ex and ex[2] == 'HALT' and int(ex[3]) == 0:
                    t52_res[(m, k)] = ex
                    reused += 1
                else:
                    t52_jobs[k].append(m)
        print(f'Starting Phase 2: {len(t52_rows)} Tier-5/2 SMALL-HALT rows ({reused} exact HALT&listcut=0 reused, {sum(len(v) for v in t52_jobs.values())} runs to execute)...', flush=True)
        new_res = execute_jobs('t52_ht', t52_jobs)
        t52_res.update(new_res)
        summarize_rows('Phase 2: Tier-5 & Tier-2 SMALL-HALT', t52_rows, cands, t52_res, os.path.join(HERE, 'tier5_sh_results.tsv'))


if __name__ == '__main__':
    main()
