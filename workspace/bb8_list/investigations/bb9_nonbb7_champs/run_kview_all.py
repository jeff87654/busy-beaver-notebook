import sys, os, subprocess, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

KVIEW = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits\kview.exe'
DLSCAN2 = r'C:\Users\jeffr\Downloads\bb8\bb8_list\neighbors\dlscan2.exe'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)

CHAMPS = [
    ("FamE", "1RB0RA_1LC1RF_1RE0LD_0LC0LE_1RA---_1RD0LG_0RF0RG", "R,E,P=1,u=10,s=1,d=1d+1,b=2b+2,S=-"),
    ("FamF", "1RB1LC_0LA0LD_1LA1LF_1RE0RB_1RF1LE_1RG0RC_0RF---", "R,A,P=10,u=01,s=10,d=1d+0,b=1b+0,S=-"),
    ("C1_bb7", "1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF", "R,B,P=11,u=10,s=1,d=3d+1,b=3b+2,S=111001"),
    ("C1_new", "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF", "R,B,P=11,u=10,s=1,d=3d+1,b=3b+2,S=111001"),
    ("C2_L1", "1RB---_1LC1LE_1LD0LC_0RE0LA_0LF0RF_1RF1RG_1LB1RB", "L,D,P=1,u=0011,s=01,d=1d+0,b=1b+0,S=000000001"),
    ("C2_L2", "1RB---_1LC1LE_1LD0LC_0RE0LA_1LB0RF_1RF1RG_1LB1RB", "L,D,P=1,u=0011,s=01,d=1d+0,b=1b+0,S=00000001"),
    ("C2_R1", "1RB0LE_1RC1RA_1RD0RC_0LA0RG_1LE1LF_1RB1LB_1LB---", "R,D,P=1,u=0011,s=01,d=1d+0,b=1b+0,S=00000001"),
    ("C2_R2", "1RB0LE_1RC1RA_1RD0RC_0LA1RG_1LE1LF_1RB1LB_0RC---", "R,D,P=1,u=0011,s=01,d=1d+0,b=1b+0,S=00000001"),
    ("C3_1", "1RB---_1LC0LG_1RF1RD_0RF0LE_0LC1LB_1RA0RC_1LB0LE", "L,B,P=101,u=10,s=00,d=1d+0,b=2b+1,S=1"),
    ("C3_2", "1RB---_1LC0LG_1RF1RD_0RF0LE_0LC1LB_1RA0RC_1RB0LE", "L,B,P=101,u=10,s=00,d=1d+0,b=2b+1,S=1"),
    ("C3_3", "1RB0LE_1LC0LA_1RF1RD_0RF0LE_0LC1LB_1RG0RC_1RB---", "L,C,P=101,u=10,s=00,d=1d+0,b=2b+1,S=11"),
    ("C4_1", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB", "L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1"),
    ("C4_2", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB", "L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1"),
    ("C5_1", "1RB0RB_1RC1RG_1LD---_1RA1LE_0RF0LE_1LC0RF_0LD1RD", "L,E,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
    ("C5_2", "1RB0RB_1RC1RG_1LD---_1RA1LE_0RF0LE_1LC0RF_0LF1RD", "L,E,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
    ("C5_3", "1RB1LD_1RC0RF_1LA---_0RE0LD_1LC0RE_0LA1RG_0LA1RA", "L,D,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
    ("C5_4", "1RB1LD_1RC0RF_1LA---_0RE0LD_1LC0RE_0RA1RG_0LA1RA", "L,D,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
    ("C5_5", "1RB1LD_1RC0RF_1LA---_0RE0LD_1LC0RE_1LF1RG_0LA1RA", "L,D,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
    ("C5_6", "1RB1LD_1RC0RF_1LA---_0RE0LD_1LC0RE_1LF1RG_0LE1RA", "L,D,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
]

def parse_tmpl_str(t):
    parts = t.split(',')
    side, st = parts[0], parts[1]
    kv = dict(p.split('=') for p in parts[2:])
    al, be = map(int, re.match(r'(\d+)d\+(\d+)', kv['d']).groups())
    alB, beB = map(int, re.match(r'(\d+)b\+(\d+)', kv['b']).groups())
    return [side, st, kv['P'], kv['u'], kv['s'], str(al), str(be), str(alB), str(beB), kv['S']]

for tag, m, tmpl in CHAMPS:
    args = parse_tmpl_str(tmpl)
    r = subprocess.run([KVIEW, m] + args + ['10000000', '25'], capture_output=True, text=True, creationflags=LOW)
    print(f"=== {tag}: {m} ({tmpl}) ===")
    for line in r.stdout.splitlines()[:15]:
        print("  " + line)
