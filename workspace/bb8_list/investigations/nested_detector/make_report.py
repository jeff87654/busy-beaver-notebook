"""Builds ../nested_detector.md from report_body.txt, the calibration outputs and the scan outputs.

  python make_report.py

Placeholders in report_body.txt: @SUMMARY@ (summary.txt in this directory), @CALIB@ (calib_1M.tsv, calib_2e7.tsv),
@SCANS@ (scans/*/merged.tsv or out/*.tsv), @COST@ (cost.txt).
"""
import glob
import os
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'nested_detector.md'

NAMES = {
    '1RB1RA_0LC0LF_0RD1LC_1RA1RG_---0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH': 'BB(9) champion',
    '1RB1RA_0LC0LF_0RD1LC_1RA1RG_---0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ': 'BB(10) champion',
    '1RB1RA_1LH1RC_0LD0LG_0RE1LD_1RA1RF_---0RA_1LC1LG_1LJ1LI_1LK1LJ_---0LI_1RA1LH': 'BB(11) champion',
    '0LJ0RF_1LH1RC_0LD0LG_0RE1LD_1RF1RA_1RB1RF_1LC1LG_1LL1LI_1LK0LH_1RH1LJ_---1LA_1RF1LL': 'BB(12) champion',
    '1RB1RA_1LC1RD_1LA1LC_1LG0RE_1LC1RB_0RL1LG_0LM0RH_1RI1RH_1LK0RI_---0LK_1LF1LK_1LJ1RL_---1RH': 'BB(13) champion, f_{w+1}',
    '0LH0LL_1RI1RC_0LD1LG_0RE1LD_---1RF_---0RM_1RM0LH_1LG1LH_0LN0RJ_---0LK_0LK1LL_1LG1LA_1RB1RM_0LG1LN': 'BB(14) champion, f_{w+1}',
    '1LN1RI_1RA0RC_1RB1LD_0LD1LE_1LF1RG_1RH0LE_0RE1LD_1RB1RH_---0RJ_1LN0LK_0LK1LL_1LM1LM_1RH0LL_1LO1LN_0LH1LN': 'BB(15) champion, f_{w+1}',
    '1RB1RA_1RH0RC_1RB1LD_0LD1LE_1LF1RG_1RA0LE_0RE1LD_1LO1RI_---1RJ_0LO0RK_1LO0LL_0LL1LM_1RA1LN_0LM0LM_1LP1LO_0LA1LO': 'BB(16) champion, f_{w+1}',
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF': 'our BB(8) record',
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---': 'our BB(9) record',
    '1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---': '76450 Ackermann counter (non-halt)',
    '1RB0RA_0RC0RD_0LD---_1RE0LF_1RF1RD_1LE0LG_1LF1LH_0RA0LG': '240161 digit list (non-halt)',
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF': 'm7 sibling (non-halt)',
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE': 'm7 0RB0LC (non-halt)',
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF': 'BB(7) champion',
}
CLEAN = {'1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LG0LC_1RG1LD_0RH0RF_0RI0RE_---0RJ_0LB0RJ',
         '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_0LB0RE_---0LJ_0RJ0RH',
         '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_---0RE_0LB0LJ_0RJ0RI',
         '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_---0RE_0LD0RJ_0LB1RI',
         '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RI0LC_1RG1LD_0RH0RF_0LJ0RE_---0RJ_1LG0LF'}
ORDER = ['W1-HALTER', 'W1-HALT?', 'W1-LOOPER', 'MULTI', 'MULTI?', 'LOOPER', 'REBUILD', 'CHAMPION', 'R4-SOME', 'HALT?',
         'HALT-SOME', 'CHECK', 'NOBOUNDARY', 'SAFE']


def rows(path):
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path):
        if line.startswith('machine\t') or line.startswith('#') or not line.strip():
            continue
        out.append(line.rstrip('\n').split('\t'))
    return out


def calib_table():
    r1 = {r[0]: r for r in rows(HERE / 'calib_1M.tsv')}
    r2 = {r[0]: r for r in rows(HERE / 'calib_2e7.tsv')}
    lines = ['| machine | what | census 1e6 | census 2e7 | chains at 2e7 (abridged) |', '|---|---|---|---|---|']
    ms = [l.split()[0] for l in open(HERE / 'calib_nested.txt') if l.strip()]
    for i, m in enumerate(ms):
        a, b = r1.get(m), r2.get(m)
        if m in NAMES:
            name = NAMES[m]
        elif m in CLEAN or i == 15:
            name = 'rec14 clean looper (full_cycles=3)'
        elif i < 29:
            name = 'rec14 LOOP row, full_cycles=0'
        else:
            name = 'rec14 107-class looper'
        ch = (b[5] if b else '-')
        if len(ch) > 110:
            ch = ch[:110] + '...'
        lines.append(f'| `{m}` | {name} | {a[3] if a else "-"} | {b[3] if b else "-"} | `{ch}` |')
    return '\n'.join(lines)


def scan_rows(d):
    r = os.path.join(d, 'regraded.tsv')
    if os.path.exists(r):
        return rows(r), True
    m = os.path.join(d, 'merged.tsv')
    if os.path.exists(m):
        return rows(m), True
    out = []
    for f in sorted(glob.glob(os.path.join(d, 'out', '*.tsv'))):
        out += rows(f)
    return out, False


def summaries(d):
    tot = Counter()
    for f in sorted(glob.glob(os.path.join(d, 'out', '*.tsv'))):
        for line in open(f):
            if line.startswith('#summary'):
                for kv in line.split('\t')[1:]:
                    k, v = kv.strip().split('=')
                    tot[k] += int(v)
    return tot


def scan_section():
    out = []
    dirs = [('rec14 (first 36 chunks, re-graded v6)', 'scans/rec14_part1'), ('c35m14', 'scans/c35m14'), ('r10m14', 'scans/r10m14'),
            ('rec14_0RH', 'scans/rec14_0RH'), ('rec14_1RE', 'scans/rec14_1RE'), ('r10m13', 'scans/r10m13'),
            ('BB(8) holdout sample (3000)', 'scans/bb8_sample/run'),
            ('rec14 sample 300, census 2e7', 'scans/longcensus/run2e7')]
    hits = []
    out.append('Grades as recorded per scan (chunks run with v1-v6). The W1/MULTI rows were all re-graded with the final v7; see the hit table below and `scans/w1multi_v7.tsv`.')
    out.append('')
    out.append('| scan | machines | with an R1-R3 fit | grades of the fitted rows |')
    out.append('|---|---|---|---|')
    for name, rel in dirs:
        d = HERE / rel
        if not d.exists():
            continue
        rs, _ = scan_rows(str(d))
        s = summaries(str(d))
        c = Counter(r[3] for r in rs)
        g = ', '.join(f'{k} {c[k]}' for k in ORDER if c.get(k))
        out.append(f'| {name} | {s.get("machines", "?")} | {len(rs)} | {g} |')
        for r in rs:
            pass
    out.append('')
    v7 = rows(HERE / 'scans' / 'w1multi_v7.tsv')
    hits = [('all scans, v7', r) for r in v7 if r[3].startswith('W1') or r[3] == 'MULTI']
    if hits:
        out.append('Rows graded W1-* or MULTI (the MULTI? rows are listed in each scan directory regraded.tsv; chain summaries abridged):')
        out.append('')
        out.append('| scan | machine | grade | template | chains |')
        out.append('|---|---|---|---|---|')
        hits.sort(key=lambda h: ORDER.index(h[1][3]) if h[1][3] in ORDER else 99)
        for name, r in hits:
            ch = r[5] if len(r[5]) <= 150 else r[5][:150] + '...'
            out.append(f'| {name} | `{r[0]}` | {r[3]} | `{r[4][:60]}` | `{ch}` |')
    return '\n'.join(out)


def txt(name):
    p = HERE / name
    return p.read_text().strip() if p.exists() else '(pending)'


TEXT = open(HERE / 'report_body.txt').read()
TEXT = (TEXT.replace('@SUMMARY@', txt('summary.txt')).replace('@CALIB@', calib_table())
        .replace('@SCANS@', scan_section() + '\n\n' + txt('scans_notes.txt')).replace('@COST@', txt('cost.txt')))
OUT.write_text(TEXT)
print('wrote', OUT)
