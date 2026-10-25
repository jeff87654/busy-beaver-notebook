import sys, os, csv, glob
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
OUT_DIR = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_7state_fw1_redirects'
t_str = "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"
T = kl.tmpl("1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC", t_str)

print("=== 1. VERIFYING REB_E2 9-STATE GEMS WITH MAXL=50 ===")
ODD_TOP_REPS = [
    ("redir_A0_5_24_v1", "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0RB0RC_0LI1LH_0LB---", [5, 2, 2, 2, 2], 3),
    ("redir_A0_5_24_v2", "1RH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0RB0RC_0LI---_0LD1LI", [5, 2, 2, 2, 2], 3),
    ("redir_A0_5_24_v3", "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0RI0RC_0LD1LH_1RC---", [5, 2, 2, 2, 2], 3),
    ("redir_A0_3_24",    "0LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0RB0RC_1LI0LH_0LB---", [3, 2, 2, 2, 2], 3),
    ("redir_A0_3_23",    "1RF0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_1LH0RC_0LI---_0RC1LG", [3, 2, 2, 2], 1),
    ("redir_E0_5_25",    "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LH1LF_0RB1LE_1LI0RC_0RB1LG_0RD---", [5, 2, 2, 2, 2, 2], 3),
    ("redir_E1_5_25_8s", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_---0RC_0LI1LE_0RF---", [5, 2, 2, 2, 2, 2], 3),
    ("redir_E1_5_25_G0", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_0RB0RC_0LI1LE_0RG---", [5, 2, 2, 2, 2, 2], 3),
    ("redir_E1_I1_0LB",  "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_---0RC_0LI1LE_0RF0LB", [5, 2, 2, 2, 2, 2], 3),
    ("redir_E1_I1_0LD",  "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_---0RC_0LI1LE_0RF0LD", [5, 2, 2, 2, 2, 2], 3),
    ("redir_A0_E2_1LH",  "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC_0LI1LH_0LB0RB", [5, 2, 2, 2, 2], 3),
    ("redir_A0_E2_1RH",  "1RH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC_0LI0LD_0LD1LI", [5, 2, 2, 2, 2], 3),
]

for name, tm, ds_blank, a_blank in ODD_TOP_REPS:
    k_zeros = len(ds_blank) - 1
    e1_ds = [1] + [0] * k_zeros
    res_list = []
    for a in [5, 7, 9, 11, 13]:
        evs = kl.run(tm, e1_ds, a, 1, steps=50000, nchg=0, maxl=50, T=T, pall=1)
        r = next((e for e in evs[1:] if e[0] == 'H' or (e[0] == 'K' and e[4] == 1 and e[2] != e1_ds)), ('END',))
        if r[0] == 'K':
            res_list.append(f"a={a}:K({short(r[2])};{r[3]})@{r[1]}")
        elif r[0] == 'H':
            res_list.append(f"a={a}:H({r[2]}{r[3]})@{r[1]}")
        else:
            res_list.append(f"a={a}:END")
    evs_syn = kl.run(tm, [3, 2, 2], 3, 1, steps=2000000, nchg=0, maxl=200, T=T, pall=1)
    syn_last = evs_syn[-1] if evs_syn else None
    print(f"  {name:18s}: blank=K({short(ds_blank)};{a_blank}) | E1(1,0^{k_zeros}; a): {' '.join(res_list)} | syn K(3,2,2;3)->{syn_last}")

print("\n--- Tracing Round 2 of redir_E1_I1_0LD and redir_A0_E2_1LH/1RH ---")
for name, tm, ds_cfg, a_cfg in [
    ("redir_E1_I1_0LD inner1 [7,0,0,1; 9]", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_---0RC_0LI1LE_0RF0LD", [7, 0, 0, 1], 9),
    ("redir_E1_I1_0LD inner1 [7,1,0,0; 9]", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_---0RC_0LI1LE_0RF0LD", [7, 1, 0, 0], 9),
    ("redir_E1_I1_0LD E2 [1,0,0,0,0,1; 9]", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_---0RC_0LI1LE_0RF0LD", [1, 0, 0, 0, 0, 1], 9),
    ("redir_A0_E2_1LH inner3 [5,2,1,0; 9]", "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC_0LI1LH_0LB0RB", [5, 2, 1, 0], 9),
    ("redir_A0_E2_1LH inner1 [5,0,0,1; 9]", "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC_0LI1LH_0LB0RB", [5, 0, 0, 1], 9),
    ("redir_A0_E2_1LH E2 [1,0,0,0,1; 9]",   "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC_0LI1LH_0LB0RB", [1, 0, 0, 0, 1], 9),
    ("redir_A0_E2_1RH inner1 [5,0,0,1; 9]", "1RH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC_0LI0LD_0LD1LI", [5, 0, 0, 1], 9),
    ("redir_A0_E2_1RH E2 [1,0,0,0,1; 9]",   "1RH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC_0LI0LD_0LD1LI", [1, 0, 0, 0, 1], 9),
]:
    evs = kl.run(tm, ds_cfg, a_cfg, 1, steps=50000, nchg=0, maxl=50, T=T, pall=1)
    r = next((e for e in evs[1:] if e[0] == 'H' or (e[0] == 'K' and e[4] == 1 and e[2] != ds_cfg)), ('END',))
    print(f"  {name:38s} -> {r}")

print("\n=== 2. AUDITING c209_plus_dl3.tsv GEMS ===")
dl2_files = sorted(glob.glob(r'C:\Users\jeffr\Downloads\bb8\bb8_list\dl2_out\c*.tsv'))
print(f"Latest dl2_out file: {os.path.basename(dl2_files[-1])}")

with open(os.path.join(OUT_DIR, 'c209_plus_dl3.tsv'), 'r') as f:
    rd = csv.DictReader(f, delimiter='\t')
    rows = list(rd)

interesting = [r for r in rows if r['verdict'] in ('CHAMPION', 'MULTI?', 'W1-LOOPER', 'REBUILD', 'HALT-SOME')]
print(f"Auditing {len(interesting)} machines in c209_plus_dl3.tsv:")
for r in interesting:
    tm = r['tm']
    verdict = r['verdict']
    t = r['template']
    if not t or t == '-':
        print(f"  [{verdict}] {tm} (no template)")
        continue
    T_cur = kl.tmpl(tm, t)
    b_res = kl.blank(tm, steps=200000, maxl=60, T=T_cur)
    max_len = max((len(l[2]) for l in b_res if l[0] == 'K'), default=0)
    first_deep = next((l for l in b_res if l[0] == 'K' and len(l[2]) >= 4), b_res[0] if b_res else None)
    last_l = b_res[-1] if b_res else None
    B_val = first_deep[4] if (first_deep and first_deep[0] == 'K') else 1
    e_summary = []
    for a in range(1, 6):
        res_e = kl.run(tm, [], a, B_val, steps=50000, nchg=0, maxl=15, T=T_cur, pall=1)
        nxt = next((e for e in res_e[1:] if e[0] == 'H' or (e[0] == 'K' and e[4] == B_val and e[2] != [])), res_e[-1] if res_e else None)
        if nxt and nxt[0] == 'K':
            e_summary.append(f"a={a}->K({short(nxt[2])};{nxt[3]})@{nxt[1]}")
        elif nxt and nxt[0] == 'H':
            e_summary.append(f"a={a}->H({nxt[2]}{nxt[3]})@{nxt[1]}")
        elif nxt:
            e_summary.append(f"a={a}->{nxt[0]}@{nxt[1]}")
    fd_str = f"K({short(first_deep[2])};{first_deep[3]};{first_deep[4]})@{first_deep[1]}" if (first_deep and first_deep[0] == 'K') else str(first_deep)
    ll_str = f"K({short(last_l[2])};{last_l[3]};{last_l[4]})@{last_l[1]}" if (last_l and last_l[0] == 'K') else str(last_l)
    print(f"  [{verdict:9s}] {tm} | tmpl={t} | max_len={max_len} | first4+={fd_str} | last={ll_str}")
    print(f"              E(;a;{B_val}): {' | '.join(e_summary)}")
