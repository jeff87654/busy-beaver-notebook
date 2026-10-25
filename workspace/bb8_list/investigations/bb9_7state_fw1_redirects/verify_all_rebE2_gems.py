import sys, os, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
HERE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_7state_fw1_redirects'
tsv = os.path.join(HERE, 'enum_rebE2_9.tsv')
t_str = "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"
T = kl.tmpl("1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC", t_str)

print("=== 1. Verifying exact mechanisms of ODD-TOP E1_HALT machines (redir=A0, E0, E1, D0) ===")
ODD_TOP_REPS = [
    ("redir_A0_5_24_v1", "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0RB0RC_0LI1LH_0LB---", [5, 2, 2, 2, 2], 3),
    ("redir_A0_5_24_v2", "1RH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0RB0RC_0LI---_0LD1LI", [5, 2, 2, 2, 2], 3),
    ("redir_A0_5_24_v3", "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0RI0RC_0LD1LH_1RC---", [5, 2, 2, 2, 2], 3),
    ("redir_A0_3_24",    "0LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0RB0RC_1LI0LH_0LB---", [3, 2, 2, 2, 2], 3),
    ("redir_A0_3_23",    "1RF0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_1LH0RC_0LI---_0RC1LG", [3, 2, 2, 2], 1),
    ("redir_E0_5_25",    "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LH1LF_0RB1LE_1LI0RC_0RB1LG_0RD---", [5, 2, 2, 2, 2, 2], 3),
    ("redir_E1_5_25_8s", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_---0RC_0LI1LE_0RF---", [5, 2, 2, 2, 2, 2], 3),
    ("redir_E1_5_25_G0", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_0RB0RC_0LI1LE_0RG---", [5, 2, 2, 2, 2, 2], 3),
]

for name, tm, ds_blank, a_blank in ODD_TOP_REPS:
    k_zeros = len(ds_blank) - 1
    e1_ds = [1] + [0] * k_zeros
    res_list = []
    for a in [5, 7, 9, 11, 13]:
        evs = kl.run(tm, e1_ds, a, 1, steps=20000, nchg=0, maxl=10, T=T, pall=1)
        r = next((e for e in evs[1:] if e[0] == 'H' or (e[0] == 'K' and e[4] == 1 and e[2] != e1_ds)), ('END',))
        res_list.append(f"a={a}:{r[0]}@{r[1]}" if len(r) > 1 else f"a={a}:END")
    # Also test synthetic small configuration K(3, 2; 3; 1) to full halt!
    evs_syn = kl.run(tm, [3, 2], 3, 1, steps=2000000, nchg=0, maxl=100, T=T, pall=1)
    syn_last = evs_syn[-1] if evs_syn else None
    print(f"  {name:18s}: blank=K({short(ds_blank)};{a_blank}) | E1(1,0^{k_zeros}; a): {' '.join(res_list)} | syn K(3,2;3)->{syn_last}")

print("\n=== 2. Checking EVEN-TOP E1_HALT machines on K(0^k; a; 1) ===")
EVEN_TOP_REPS = [
    ("even_2_9_0", "1LB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0LH0RC_1LI---_1LA1LG", [2]*9 + [0], 9),
    ("even_2_8",   "1LB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0LH0RC_1LI---_0LF1LG", [2]*8, 2),
    ("even_2_10",  "1RB0RG_1RC1RA_1RD1RC_0LH0LF_0LF1LF_0RB1LE_1LE0RC_0LI1LH_0RF---", [2]*10, 3),
]
for name, tm, ds_blank, a_blank in EVEN_TOP_REPS:
    res_0 = []
    for a in [5, 7, 9, 11]:
        evs = kl.run(tm, [], a, 1, steps=20000, nchg=0, maxl=10, T=T, pall=1)
        r = next((e for e in evs[1:] if e[0] == 'H' or (e[0] == 'K' and e[4] == 1 and e[2] != [])), ('END',))
        res_0.append(f"a={a}:{r[0]}({ short(r[2]) if r[0]=='K' else r[2]+str(r[3]) })@{r[1]}" if len(r) > 1 else f"a={a}:END")
    print(f"  {name:14s}: blank=K({short(ds_blank)};{a_blank}) | E(0^k; a): {' '.join(res_0)}")
