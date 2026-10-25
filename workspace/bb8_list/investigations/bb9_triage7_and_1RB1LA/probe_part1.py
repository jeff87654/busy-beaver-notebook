import sys, os, subprocess, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

HERE = os.path.dirname(os.path.abspath(__file__))
KV1 = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits\kview.exe'
KV2 = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits\kview2.exe'

dl3_tr_out = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_triage7\out.tsv'
new_dl3_out = os.path.join(HERE, 'new_dl3_out.tsv')

rows = {}
for p in (dl3_tr_out, new_dl3_out):
    with open(p, 'r', encoding='utf-8') as f:
        for l in f:
            l = l.rstrip('\r\n')
            if not l or l.startswith('machine\t') or l.startswith('#'): continue
            parts = l.split('\t')
            rows[parts[0]] = parts

def parse_tmpl(t):
    o, q, rest = t.split(',', 2)
    d = dict(x.split('=', 1) for x in rest.split(','))
    al, be = map(int, re.fullmatch(r'(\d+)d\+(-?\d+)', d['d']).groups())
    alB, beB = map(int, re.fullmatch(r'(\d+)b\+(-?\d+)', d['b']).groups())
    return [o, q, d['P'], d['u'], d['s'], str(al), str(be), str(alB), str(beB), d['S']]

TARGETS = [
    # 5 R4-SOME
    ("r4_1_rrrr", "1RB0RD_0LC1LC_1LE1LD_1RE1LB_1RG1LF_---0LE_1RA1RG"),
    ("r4_2_rrFFr", "1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA0LE"),
    ("r4_3_rrFFr", "1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA1RB"),
    ("r4_4_rFrL", "1RB0RD_0RC1RG_1RD1RC_1LD0LE_0RB1LF_0LC1LE_---1RA"),
    ("r4_5_P11", "1RB0LC_0RC1LC_0RD1LA_1RE---_0LC0RF_1LD1RG_1RF1RB"),
    # MULTI and W1-LOOPER
    ("multi_1", "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF"),
    ("w1loop_1", "1RB0RE_1RC1RA_0LD0LE_1RE0LE_0RF1LC_1LC1RG_0RB---"),
    # Multiplicative REBUILD
    ("reb_A1", "1RB---_1RC0RG_1RD1RA_0LE0RF_1LG0LF_0RD1LB_1RE0LF"),
    ("reb_A2", "1RB0RC_1LA0RC_0LG1RD_1LE0LB_1LG1LF_1LD---_0RA0LC"),
    ("reb_A3", "1RB0RG_1RC1RF_0LD0RE_1LG0LE_0RC1LA_1RA---_1RD0LE"),
    ("reb_B1", "1RB0LA_1LC1LG_0LD1LB_1RE0RB_0RF1RF_0LA0RE_0LC---"),
    ("reb_B2", "1RB0LE_1LC1LG_0LD1LB_1RE0RB_0RF1RF_0LA0RE_0LC---"),
    ("reb_C1", "1RB0LC_1LA0LC_0RD1LE_0LB0RC_1RF0RA_1RD1RG_1RE---"),
    ("reb_D1", "1RB0RD_1RC---_0RD1RA_0RE0RA_0LF0LE_1LG0RE_0LA1LF"),
    ("reb_D2", "1RB0RD_1RC---_1LC1RA_0RE0RA_0LF0LE_1LG0RE_0LA1LF"),
    ("reb_E1", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RA0RG_---0RB"),
    ("reb_E2", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC"),
    ("reb_F1", "1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA"),
    # Champions
    ("champ_402", "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF"),
    ("champ_231", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"),
    # Sample HALT-SOME & additive REBUILD
    ("hs_1", "1RB0LB_1LC0RA_0LD1RC_1LE1LD_0RB0RF_---0RG_1RF1LB"),
    ("hs_2", "1RB0LE_0RC1LB_1RD1RC_0LA0LF_1LA0RD_---0LG_1LF0RE"),
    ("reb_add1", "1RB---_1RC0RF_1LD1LE_0RE0LC_1RF0RG_1LE1RA_1RE0LC"),
    ("reb_add2", "1RB0LC_1LB1RA_0RG1LD_0LE1LC_0RF0LG_0RB1RE_---1RF"),
]

with open(os.path.join(HERE, 'probe_part1.out'), 'w', encoding='utf-8') as fo:
    for tag, tm in TARGETS:
        parts = rows[tm]
        targs = parse_tmpl(parts[4])
        cmd = [KV1, tm] + targs + ['100000000', '30', '0']
        p = subprocess.Popen(cmd, creationflags=0x40, stdout=subprocess.PIPE, text=True)
        out, _ = p.communicate()
        fo.write(f"\n=== {tag}: {tm} ({parts[3]}) | {parts[4]} | {parts[6]} ===\n")
        for l in out.splitlines()[:30]:
            fo.write("  [KV1] " + l + "\n")
        if any(' ? ' in l for l in out.splitlines()) or len(out.splitlines()) <= 3:
            targs_star = list(targs)
            targs_star[2] = '*'
            cmd2 = [KV2, tm] + targs_star + ['50000000', '20', '0']
            p2 = subprocess.Popen(cmd2, creationflags=0x40, stdout=subprocess.PIPE, text=True)
            out2, _ = p2.communicate()
            for l in out2.splitlines()[:20]:
                fo.write("  [KV2] " + l + "\n")
        fo.flush()
print("Done probe_part1.py")
