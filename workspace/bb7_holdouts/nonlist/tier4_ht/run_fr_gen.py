"""run_fr_gen.py: Run nlp7_fr_gen.exe on all 932 Tier-4 rows:
  1) Blank-tape generalized frontier-decrement scan (1,000,000 macro steps at K in {'2', DK, SRK, pilot_K}):
     checks FR1 (step -1), FR2 (step -2), FR3 (step -3), FR46 (step -4..-6), FRref (refilled after slow dec), FRpair (2-run sum dec).
  2) Glitch-safe HT scan (--htsafe, 5,000,000 macro steps) to check whether iv.clear() at list exhaustion hid any HT >= 3.
Uses W=2 Idle workers (creationflags=0x40).
"""
import collections
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
NONLIST = os.path.dirname(HERE)
EXE = os.path.join(HERE, 'nlp7_fr_gen.exe')
PIDS_LOG = os.path.join(HERE, 'pids_tier4.txt')
W = 2


def main():
    cands = {l.split('\t')[1]: l.rstrip('\n').split('\t') for l in open(os.path.join(NONLIST, 'cands.tsv')) if not l.startswith('class')}
    final_rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(NONLIST, 'final.tsv')) if not l.startswith('tier')]
    t4_rows = [r for r in final_rows if r[0] == '4']

    jobs_by_k = collections.defaultdict(list)
    for r in t4_rows:
        m = r[3]
        c = cands[m]
        for k in sorted({'2', r[6], c[7], c[3]} - {'-'}):
            jobs_by_k[k].append(m)

    # 1. Run blank-tape generalized FR scan (1M macro steps)
    tasks = []
    for k in sorted(jobs_by_k):
        ms = jobs_by_k[k]
        for idx, i in enumerate(range(0, len(ms), 250)):
            tasks.append(('frgen', k, idx, ms[i:i + 250]))

    def run_one(args):
        mode, k, idx, ms = args
        inp = os.path.join(HERE, f'{mode}_K{k}_c{idx:02d}.txt')
        out = os.path.join(HERE, f'{mode}_K{k}_c{idx:02d}.tsv')
        with open(inp, 'w') as f:
            f.write('\n'.join(ms) + '\n')
        cmd = [EXE, inp, out, '1000000' if mode == 'frgen' else '5000000', f'--K={k}']
        if mode == 'htsafe':
            cmd.append('--htsafe')
        p = subprocess.Popen(cmd, creationflags=0x40, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.wait()
        return mode, k, out

    t0 = time.time()
    with ThreadPoolExecutor(W) as ex:
        res_files = list(ex.map(run_one, tasks))
    print(f'frgen scan done in {time.time() - t0:.1f}s', flush=True)

    fr_map = collections.defaultdict(list)
    for mode, k, out in res_files:
        for l in open(out):
            f = l.rstrip('\n').split('\t')
            if len(f) >= 11:
                fr_map[f[0]].append((k, f[2], int(f[3]), int(f[4]), int(f[5]), int(f[6]), int(f[7]), int(f[8]), int(f[9]), int(f[10])))

    with open(os.path.join(HERE, 'tier4_fr_gen.tsv'), 'w') as o:
        o.write('machine\tD\tDK\tSRs\tmax_FR1\tmax_FR2\tmax_FR3\tmax_FR46\tmax_FRref\tmax_FRpair\tdetails\tshape\n')
        fr2_hits, fr3_hits, fr46_hits, frref_hits, frpair_hits = [], [], [], [], []
        for r in t4_rows:
            m = r[3]
            d = int(r[5])
            entries = fr_map[m]
            m1 = max((x[4] for x in entries), default=0)
            m2 = max((x[5] for x in entries), default=0)
            m3 = max((x[6] for x in entries), default=0)
            m46 = max((x[7] for x in entries), default=0)
            mref = max((x[8] for x in entries), default=0)
            mpair = max((x[9] for x in entries), default=0)
            det = '; '.join(f'K{x[0]}:fr1={x[4]},fr2={x[5]},fr3={x[6]},fr46={x[7]},ref={x[8]},pair={x[9]}' for x in entries if any(x[4:]))
            if not det:
                det = '-'
            o.write(f'{m}\t{d}\t{r[6]}\t{r[10]}\t{m1}\t{m2}\t{m3}\t{m46}\t{mref}\t{mpair}\t{det}\t{r[13]}\n')
            if m2 > 0:
                fr2_hits.append((d, m2, mref, m, det, r[13][:90]))
            if m3 > 0:
                fr3_hits.append((d, m3, mref, m, det, r[13][:90]))
            if m46 > 0:
                fr46_hits.append((d, m46, mref, m, det, r[13][:90]))
            if mref > 0:
                frref_hits.append((d, mref, m2, m3, m46, m, det, r[13][:90]))
            if mpair > 0:
                frpair_hits.append((d, mpair, mref, m, det, r[13][:90]))

    print(f'Tier-4 generalized frontier decrements (total 932 rows, 800 with D>=15):')
    print(f'  FR2 (step -2) > 0: {len(fr2_hits)} (D>=15: {sum(1 for x in fr2_hits if x[0] >= 15)})')
    for x in fr2_hits[:25]:
        print(f'    [FR2] D={x[0]} FR2={x[1]} ref={x[2]} {x[3]} | {x[4]} | {x[5]}')
    print(f'  FR3 (step -3) > 0: {len(fr3_hits)} (D>=15: {sum(1 for x in fr3_hits if x[0] >= 15)})')
    for x in fr3_hits[:25]:
        print(f'    [FR3] D={x[0]} FR3={x[1]} ref={x[2]} {x[3]} | {x[4]} | {x[5]}')
    print(f'  FR46 (step -4..-6) > 0: {len(fr46_hits)} (D>=15: {sum(1 for x in fr46_hits if x[0] >= 15)})')
    for x in fr46_hits[:15]:
        print(f'    [FR46] D={x[0]} FR46={x[1]} ref={x[2]} {x[3]} | {x[4]} | {x[5]}')
    print(f'  FRref (refilled after slow dec) > 0: {len(frref_hits)}')
    for x in frref_hits[:25]:
        print(f'    [FRref] D={x[0]} ref={x[1]} fr2={x[2]} fr3={x[3]} fr46={x[4]} {x[5]} | {x[6]} | {x[7]}')
    print(f'  FRpair (2-run sum step -1..-4) > 0: {len(frpair_hits)} (D>=15: {sum(1 for x in frpair_hits if x[0] >= 15)})')
    for x in frpair_hits[:25]:
        print(f'    [FRpair] D={x[0]} FRpair={x[1]} ref={x[2]} {x[3]} | {x[4]} | {x[5]}')


if __name__ == '__main__':
    main()
