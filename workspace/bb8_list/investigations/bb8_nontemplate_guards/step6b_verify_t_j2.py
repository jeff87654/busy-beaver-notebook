import os, sys, subprocess

M8_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_m8sweep"
OUR_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_nontemplate_guards"
OUT_DIR = os.path.join(OUR_DIR, "scr_x33")
WF = os.path.join(M8_DIR, "wf8.exe")
CREATE_FLAGS = 0x08000000 | 0x40

# Test the representative J=2 / J=3 T(J>0) machines with --maxt 2e7 --maxs 2e7
TEST_CASES = [
    ("X33_F0_0R",  "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0RH1LG_---0LE_1LA1RH", "R,B,P=-,u=1,s=0,d=1d+0,b=3b+2,S=-", "33", "33", "F0", os.path.join(OUT_DIR, "470_F0_c33_snap.txt")),
    ("Z16_F0_1R",  "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1RH1LG_---0LE_---0RD", "R,B,P=-,u=1,s=0,d=1d+0,b=3b+2,S=-", "33", "33", "F0", os.path.join(OUT_DIR, "476_F0_c33_snap.txt")),
    ("Y19_F0_g0",  "1RB1RA_0RC0RA_0LD1RC_0LE1LE_---1LF_1LH0LG_1LB1LG_0RA1RA", "R,A,P=-,u=1,s=0,d=1d+0,b=3b+0,S=1", "43", "43", "F0", os.path.join(OUT_DIR, "459_F0_c43_snap.txt")),
    ("F70_F0_0R",  "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0RH0LE_1RA---_0RB1RH", "R,C,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", "19", "19", "F0", os.path.join(OUT_DIR, "481_F0_c19_snap.txt")),
    ("F70_F0_1L",  "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LH0LE_1RA---_1LG---", "R,C,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", "19", "19", "F0", os.path.join(OUT_DIR, "481_F0_c19_snap.txt")),
    ("F279_B1_g0", "1RB0LA_0RC0RH_1RD---_0LE0LF_1LE0RF_1LF1RA_0RD0RG_0RD0RG", "L,A,P=-,u=1,s=0,d=1d+0,b=3b+2,S=000", "33", "33", "B1", os.path.join(OUT_DIR, "084_B1_c33_snap.txt")),
]

print("=================================================================")
print("1. DEEP VERIFICATION (--maxt 2e7) OF J=2/J=3 TIMEOUTS")
print("=================================================================")

for label, m, tmpl, c, r0, X, snapf in TEST_CASES:
    cmd = [WF, m, tmpl, '--rc', '10', '--rk', '1', '--cls', c, '60', '--R0', r0,
           '--x', X, '--from', snapf, '--maxt', '2e7', '--maxs', '2e7',
           '--loop', '--slit', '3e6', '--maxexact', '2e7', '--xmax', '50000', '--tapemax', '5e7']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=CREATE_FLAGS, cwd=OUR_DIR)
    out, _ = p.communicate()
    print(f"  [{label}] {out.strip()}")
