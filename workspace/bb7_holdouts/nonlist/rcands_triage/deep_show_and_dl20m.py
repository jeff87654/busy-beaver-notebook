"""deep_show_and_dl20m.py:
1. Run nlp7v.exe 2000000 --life --K=<k> --show=5 on all key candidates across:
   - HT >= 2 / max_HT >= 2 (in rcands_snap.tsv and fr_ext_triage.tsv)
   - Tier-1 (FR > 0 & D >= 4) in rcands_snap.tsv (all FR >= 11, all SMALL-HALT, all HT >= 1, all FR2/FR3/FR46 > 0, plus cluster reps for FR 7..10)
   - D >= 15 with FR2 > 0, FR3 > 0, FR46 > 0, or high FRref in rcands_snap.tsv
2. Run dlscan3.exe (CENSUS=20000000, N=50000) on the top 40 FR>0 / high-D candidates to check for ultra-late-blooming (>3M..20M literal steps) digit lists.
Strict rules: creationflags = 0x08000000 | 0x40, W = 2 workers.
"""
import os, subprocess, time
from concurrent.futures import ThreadPoolExecutor

TRIAGE = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\rcands_triage'
NONLIST = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
NLP7V = os.path.join(NONLIST, 'nlp7v.exe')
DLSCAN3 = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\nested_detector\dlscan3.exe'
FLAGS = 0x08000000 | 0x40
W = 2

SHOW_TARGETS = [
    # Group 1: HT >= 2 / max_HT >= 2
    ('HT4_SR_T5', '1RB---_1LC1RB_1RA1LD_0LC0LE_0RG1LF_0LG0RB_1RE0LF', [2, 6]),
    ('HT2_SR_T5', '1RB---_0LC1RG_0LG1RD_0RE0RD_0RF1RE_1LF1LC_1RA0RB', [2, 3]),
    ('HT2_FR_T3', '1RB---_0RC0RB_1LC1LD_1RE0LD_1RA1RF_1RE1RG_0LE0RF', [2, 6]),
    ('HT3_EXT_H4sib', '1RB0RE_1LC1RA_0LG1LD_0RB0RG_0RF---_1RC0RC_1LD0LB', [2, 6]),
    ('HT2_EXT_SH', '1RB0RC_0LC0LB_0LD1LC_0LE1LA_0RF1LG_1RF1RA_---0LA', [2, 6]),
    ('HT2_EXT_T3', '1RB0LE_0LC0RF_1RD1LB_1LA0RB_0LD0LA_0RA0RG_0RC---', [2, 6]),

    # Group 2: Tier-1 (FR > 0 & D >= 4) in rcands_snap.tsv
    ('T1_D3169_FR99', '1RB---_0RC0RG_1LD0RC_1LE0LE_0LF0LD_1LA1LG_1RB1LE', [6, 2]),
    ('T1_D181_FR7_rep', '1RB---_1LC1RE_0LD0LC_1RD1LB_0RF0LB_1RA1RG_0RB0RB', [4, 2]),
    ('T1_D180_FR7_rep', '1RB---_1RC0LD_1RD0RF_1LE0LG_1LB1LE_1RA0RB_1LB1LB', [6]),
    ('T1_D145_FR8_rep', '1RB---_1RC1LC_1RD0LG_1RE0LF_1LD0RG_1LB0LD_1RB0RA', [6, 2]),
    ('T1_D92_FR7_SH', '1RB---_1LC1LB_1RD0LB_0LA1RE_1RC0RF_0RG1RF_0RD1RF', [2, 4]),
    ('T1_D58_FR8_rep', '1RB0LA_0RC1RD_1LD0RA_1LE0RF_1LA0LD_0LB1RG_---1RC', [2, 6]),
    ('T1_D46_FR10_SH', '1RB---_0RC1RG_1LD1RB_0LE0LD_0RF0LC_1RF0RA_0LF1RE', [2, 4]),
    ('T1_D45_FR8_rep', '1RB---_0LC0LD_0LD1RD_1LE1LF_0LF1LC_1RG0LE_0RF0RA', [2, 6]),
    ('T1_D34_FR47_FR2', '1RB---_1LC1LE_1RD0LB_1RB0RC_1RF0RC_1RG1RE_1RB0RA', [2, 6]),
    ('T1_D34_FR9_SH', '1RB---_0RC0LA_1LD0RG_1LE1RD_0LF0LD_1LB0LF_1RC0LA', [2, 6]),
    ('T1_D25_FR47_HT1', '1RB---_1RC1LC_1RD0RF_1LE1LC_1RG0LF_1RE0LD_0LB0RA', [6, 2]),
    ('T1_D22_FR38', '1RB---_1RC0LD_0LD0RG_0LG1LE_1LC0RF_0RE1RF_1RA0LG', [6]),
    ('T1_D21_FR18', '1RB---_1LC0RF_1LG0LD_1LE0RF_1RE0LB_1RD0RD_0LE0LA', [2, 4]),
    ('T1_D18_FR13', '1RB---_1LC1LG_0LD0LB_1LE0RF_1RD0LA_1RG0RC_0RC0RE', [2, 4]),
    ('T1_D16_FR10_SH', '1RB---_1RC1RF_1LD0RB_1LE0LC_1RB1LF_1RG0LE_0LG0RA', [2, 6]),
    ('T1_D16_FR8_cluster', '1RB0LB_0RC1RC_1LD1RB_1LE0LF_0LA1LE_---0LG_1RA1LC', [2, 6]),
    ('T1_D15_FR114_SH', '1RB---_1RC0RG_1RD0LG_1RE0RA_0RF0LD_1RG0RC_1LC0LG', [2, 4]),
    ('T1_D15_FR10_SH', '1RB---_1RC0RG_1RD0RE_1LE1LG_1LA0RF_0LD1LF_1LD1RB', [2, 6]),
    ('T1_D13_FR5451', '1RB---_1LC0RF_1LG0LD_1LE1LA_1LA0RG_1RB0RG_1RF0LC', [2, 6]),
    ('T1_D13_FR11', '1RB---_1LC1LB_1LE0LD_1LA0RF_1RF1LG_1RC1RF_0LB0LE', [6]),
    ('T1_D10_FR250', '1RB0LA_1RC1RG_0RD0RB_1RE0RA_1LF0LE_1RD0LE_0RE---', [2, 6]),
    ('T1_D10_FR12', '1RB---_1LC1LD_0LE0LD_1LE0LC_1RE1LF_1RB0RG_0RA1RF', [6]),
    ('T1_D10_FR10_SH', '1RB---_0RC1LF_0RD0RA_1LE0LG_1LF1LC_1RG0LE_0LC0RF', [2, 6]),
    ('T1_D9_FR36', '1RB---_0RC1LG_1LD0RF_1LE1LB_0LF1LC_0RG0LD_0LA1RC', [3]),
    ('T1_D9_FR12_SH', '1RB---_1LC1LD_0RD0LB_1LB1RE_1RF0RD_---0RG_1LA0LB', [2, 6]),
    ('T1_D8_FR11_FR2', '1RB---_1RC1RF_1LD0RD_0RE0LE_0LF1LF_1RG0LC_0RB1RA', [2, 4]),
    ('T1_D8_FR9_FR2', '1RB---_1LC0LB_1RD0LB_1RE0RD_0RF0RC_1RG0RA_1RB1LG', [4]),
    ('T1_D7_FR80_FR2', '1RB---_1RC0RA_1LD0RB_0LE0LC_0LF0LC_1RG0RA_1RF0LG', [6, 2]),
    ('T1_D7_FR41_SH', '1RB---_1RC0RB_0RD0RF_1RE0RA_1LF0LG_1RD0LE_1LF0LF', [2, 5]),
    ('T1_D7_FR11_SH', '1RB---_0RC1RD_0RD0RA_1LE1RC_0RB0LF_1LG0LA_0LE0LF', [2, 6]),
    ('T1_D6_FR694', '1RB0LA_0RC1RB_1RD1RE_1LA---_1LF0LB_1LA1LG_0LF1LF', [2, 6]),
    ('T1_D6_FR45_FR3', '1RB---_0RC0LC_1LD0LG_1RE0LF_1RF0RD_1LB1RA_0RG1LC', [4, 2]),
    ('T1_D6_FR8_SH', '1RB---_1RC0RA_1LC0RD_1RF1LE_1LF0LD_1RG0LE_0RB0RF', [2, 6]),
    ('T1_D5_FR45', '1RB---_1RC0LC_1LD0RF_0LE0LB_1LB1LF_1RB0RG_0RA1RF', [6]),
    ('T1_D4_FR50_HT1', '1RB---_1RC0LD_1RD0RF_1LB0LE_1LD0RA_1RC0RG_1RC1RE', [2, 6]),
    ('T1_D4_FR6589', '1RB---_1RC0LC_1LD0RF_1LB0LE_1LB0LB_0RG0RE_1RA1RC', [6]),
    ('T1_D4_FR739', '1RB---_1RC1RD_1LD0RG_1RB0LE_1RD0LF_1LB1LE_0RC1RA', [2, 6]),

    # Group 3: SR_snap D >= 15 with FR2 > 0, FR3 > 0, or high FRref / Tier-4 top D
    ('SR_D505_FR2_21', '1RB---_1LC1LE_0LD0LC_0RE1LG_1RE0RF_1LA1RB_0LA0LB', [5, 2]),
    ('SR_D303_FR3_12', '1RB---_1RC1RG_0RD1LG_1LE0RB_0LF0LE_1RA0LD_1RB0RF', [3, 2]),
    ('SR_D134_FR2_8', '1RB---_1RC0LF_0RD0RG_1LE1LA_1LB0RC_1LD1LF_0RC1RC', [4, 2]),
    ('SR_D127_FR2_9', '1RB0LA_0LC---_0LF1LD_1LE0LC_1RF0LD_1RG0RE_0RA0RD', [2, 4]),
    ('SR_D118_FR2_8', '1RB---_0RC1LE_0RD0RA_1RE1RC_1LF0LG_1RD0LE_0LC0LG', [2, 6]),
    ('SR_D61_FR2_113', '1RB0LA_1LC0LF_1RD0LB_1RE0RC_1LF1RG_0LA1LB_1RC---', [2, 4]),
    ('SR_D42_FR2_13', '1RB---_0RC0RB_0RD1RG_1LD0LE_1RA1LF_0LG1LB_0RA0LE', [5, 2]),
    ('SR_D35_FR2_8', '1RB---_0RC1LE_1LD0RG_1LB0LC_0LF0RC_1RA0LG_1RC0LA', [2, 6]),
    ('SR_D34_FR2_11', '1RB0LB_0RC1LE_1LD0RE_1LB0LF_1RC0LA_1LD0LG_---0LD', [2, 6]),
    ('SR_D22_FR2_12', '1RB---_0RC1RB_0LD0RG_1LE1LD_0LF1LC_0RA0LD_1RF0RE', [5, 2]),
    ('SR_D2351_ref11761', '1RB---_1LC1RB_1RD0LC_0LE1RA_1RF1LE_1RF1RG_0RB0RF', [5, 2]),
    ('SR_D1228_ref8289', '1RB---_1RC0LF_0RD1LD_0RE0LB_1RF0RG_1LB0RE_1RE0RA', [2, 6]),
    ('SR_T4_D2296_HT1', '1RB---_0RC0RA_1LD0LG_0LE0LD_0RF0LC_1RG1LD_1RF1RB', [6, 2]),
    ('SR_T4_D3422', '1RB---_0LC1LB_0LE0LD_1LC0RA_1RE1RF_1RA1RG_0LB0LG', [2, 6]),
]

def main():
    sub = os.path.join(TRIAGE, 'deep_shows')
    os.makedirs(sub, exist_ok=True)

    tasks = []
    for tag, m, ks in SHOW_TARGETS:
        for k in ks:
            tasks.append((tag, m, k))

    def run_show(t):
        tag, m, k = t
        inp = os.path.join(sub, f'{tag}_K{k}.in')
        out = os.path.join(sub, f'{tag}_K{k}.tsv')
        show_txt = os.path.join(sub, f'{tag}_K{k}.show.txt')
        if not os.path.exists(show_txt) or os.path.getsize(show_txt) == 0:
            with open(inp, 'w', encoding='utf-8') as f:
                f.write(m + '\n')
            with open(show_txt, 'w', encoding='utf-8') as sf:
                cmd = [NLP7V, inp, out, '2000000', '--life', f'--K={k}', '--show=5']
                p = subprocess.Popen(cmd, creationflags=FLAGS, stdout=sf, stderr=subprocess.STDOUT)
                p.wait()
        return tag, m, k, show_txt

    t0 = time.time()
    print(f"Running {len(tasks)} --show=5 trajectories across W={W} workers...", flush=True)
    with ThreadPoolExecutor(W) as ex:
        res = list(ex.map(run_show, tasks))
    print(f"--show=5 trajectories done in {time.time() - t0:.1f}s", flush=True)

    # Also run dlscan3 with 20,000,000 literal steps on all unique machines in SHOW_TARGETS
    uniq_m = sorted({m for _, m, _ in SHOW_TARGETS})
    mid = (len(uniq_m) + 1) // 2
    dl_chunks = [(0, uniq_m[:mid]), (1, uniq_m[mid:])]

    def run_dl20m(dc):
        idx, ms = dc
        inp = os.path.join(sub, f'dl3_20m_c{idx}.txt')
        out = os.path.join(sub, f'dl3_20m_c{idx}.tsv')
        if not os.path.exists(out) or os.path.getsize(out) == 0:
            with open(inp, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ms) + '\n')
            cmd = [DLSCAN3, inp, out, '20000000', '50000']
            p = subprocess.Popen(cmd, creationflags=FLAGS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            p.wait()
        return out

    t1 = time.time()
    print(f"Running dlscan3 (20M literal steps, 50k probe) on {len(uniq_m)} key candidates...", flush=True)
    with ThreadPoolExecutor(W) as ex:
        dl_outs = list(ex.map(run_dl20m, dl_chunks))
    print(f"dlscan3 20M done in {time.time() - t1:.1f}s", flush=True)

    hits = []
    for out in dl_outs:
        for l in open(out, 'r', encoding='utf-8', errors='replace'):
            if l.startswith(('machine', '#')): continue
            hits.append(l.rstrip('\n'))
    print(f"dlscan3 20M graded hits: {len(hits)}")
    for h in hits:
        print("  HIT:", h)

if __name__ == '__main__':
    main()
