import os, sys, re, collections

WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
from step5_analyze_probe_919 import rows

# Load blank_detail_919.tsv
bdet = {}
with open(os.path.join(WORKDIR, "blank_detail_919.tsv"), "r") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 6:
            tag, m, st, nK, nE, maxlen = p[0], p[1], p[2], int(p[3]), int(p[4]), int(p[5])
            bdet[m] = {
                "st": st, "nK": nK, "nE": nE, "maxlen": maxlen,
                "first_ks": p[6] if len(p) > 6 else "",
                "e_rebs": p[7] if len(p) > 7 else "",
                "last_k": p[8] if len(p) > 8 else ""
            }

for r in rows:
    r["bdet"] = bdet.get(r["m"], {})

# 1. Load std_399 classifications by running trace_leaf_v3 from step7q_exact_dp_399.py
from step7q_exact_dp_399 import trace_leaf_v3, std_399

verdicts = {}
for r in std_399:
    v, rnd, scale, detail = trace_leaf_v3(r)
    verdicts[r["m"]] = ("STD_D", v, rnd, scale, detail)

# 2. Classify all 467 other_d leaves
# Map active_other_d group numbers from step7s_all_122_detail.txt
with open(os.path.join(WORKDIR, "step7s_all_122_detail.txt"), "r", encoding="utf-8") as f:
    text = f.read()

blocks = text.split("=== Group #")[1:]
m_to_gnum = {}
for b in blocks:
    gnum = int(b[:2])
    ms = re.findall(r"m=([01A-Z_-]+)", b)
    for m in ms:
        m_to_gnum[m] = gnum

# Load exact Group B verdicts for #04, #05, #06
groupB_r2 = {
    "1RB1LA_0RH1RD_1LD1LC_1LE0RF_0LA0LC_---0RG_1RE1RG_0RC1RG",
    "1RB1LA_0RH1RC_1LF0RD_---0RE_1RF1RE_0LA0LG_1LC1LG_0RG1RE",
    "1RB1LA_0RH1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG_0RG1RC",
}

for r in rows:
    if r["in_cls53"] or not r["D_type"].startswith("OTHER_D"):
        continue
    m = r["m"]
    bd = r["bdet"]
    st = bd["st"]
    nK = bd["nK"]
    maxL = bd["maxlen"]
    if st.startswith("H:"):
        verdicts[m] = ("OTHER_D", "HALT_BLANK_1M", bd["nE"], f"steps={st[2:]}", f"Halted in blank trace at {st}, e_rebs={bd['e_rebs']}")
    elif nK == 0:
        verdicts[m] = ("OTHER_D", "INF_NEVER_K", 0, "inf", "Never visits K in 1M steps")
    elif nK >= 80 and maxL >= 80 and bd["nE"] <= 2:
        verdicts[m] = ("OTHER_D", "INF_POLY_GROWER", 0, "inf", f"Broken D appends digits at every visit (nK={nK}, maxL={maxL})")
    else:
        g = m_to_gnum[m]
        if g in {1, 2, 3, 10, 12, 16, 19, 20}:
            verdicts[m] = ("OTHER_D", "INF_D_EXPAND", 0, "inf", f"Group #{g:02d}: D replaces d by d-1, c(a) increasing list length forever")
        elif g in {4, 5, 6}:
            if m in groupB_r2:
                verdicts[m] = ("OTHER_D", "HALT", 2, "f_4 (maxL=3)", f"Group #{g:02d} (b_acc): E1(3)->[3,2,1];8 -> E2(even)->HALT")
            else:
                verdicts[m] = ("OTHER_D", "HALT", 1, f"f_{maxL+1} (maxL={maxL})", f"Group #{g:02d} (b_acc): {bd['first_ks'].split(' -> ')[0]} -> E1(even)->HALT")
        elif g == 27:
            verdicts[m] = ("OTHER_D", "HALT", 2, "f_omega(27^27^43)", "Group #27 (b_acc mod-3 flip): E1(1)->[3,1];12->[1];A3(even)->[3,2^N];3->[6K+3];4->E2(even)->HALT")
        elif g == 44:
            verdicts[m] = ("OTHER_D", "HALT", 1, "f_4 (maxL=4)", "Group #44 (b=1 even-a invariant): [1,2,1,89];48;1 -> E1(even)->HALT")
        elif g == 43:
            verdicts[m] = ("OTHER_D", "HALT", 4, "steps=19273629", "Group #43 (2-adic empty-list walk): E1(15)->E2(75)->E3(345)->E4(1560)->HALT @19,273,629")
        elif g == 55:
            verdicts[m] = ("OTHER_D", "HALT", 2, "steps=51591913", "Group #55: E1(2)->[2^3];2->E2(2557)->HALT @51,591,913")
        elif g in {11, 14}:
            verdicts[m] = ("OTHER_D", "HALT", 1, "steps=~5831000", f"Group #{g:02d}: E1(1)->[1,3,2,3];3->[1,3,2,1];24->HALT @~5.83M")
        elif g in {7, 8}:
            verdicts[m] = ("OTHER_D", "HALT", 1, "steps=~1.16e8", f"Group #{g:02d}: E1(1)->[3];4->[1];13->[3^8,1];15->HALT @~1.16e8")
        elif g == 26:
            verdicts[m] = ("OTHER_D", "HALT", 1, "steps=5074767", "Group #26 (2-adic [1,0] walk): [1,0];58->[1,0];799(odd)->HALT @5,074,767")
        elif g == 42:
            verdicts[m] = ("OTHER_D", "HALT", 1, "steps=~3.8e14", "Group #42 (2-adic [1,0] walk): [1,0];112->1528->20644->278710->3762601(odd)->HALT")
        elif g in {25, 33, 47}:
            verdicts[m] = ("OTHER_D", "HALT", 1, "steps=~3e16", f"Group #{g:02d}: [41];9 41-step atomic countdown -> [];251724407(bl=1)->HALT")
        elif g in {21, 28, 30, 34, 37, 41, 45, 48, 50, 52}:
            verdicts[m] = ("OTHER_D", "INF_EMPTY_E_LOOP", 0, "inf", f"Group #{g:02d}: parity-locked empty-list E(a) loop")
        elif g in {18, 40}:
            verdicts[m] = ("OTHER_D", "INF_LOOP_LEN1", 0, "inf", f"Group #{g:02d}: [1];a -> [1];3a+6 forever")
        elif g in {15, 17, 22, 39}:
            verdicts[m] = ("OTHER_D", "INF_LIST_DOUBLE", 0, "inf", f"Group #{g:02d}: exponential list-length doubler [2^L] -> [2^(2L+c)]")
        elif g in {9, 13, 31, 35, 38, 46, 49, 51, 53, 54, 56, 57}:
            verdicts[m] = ("OTHER_D", "INF_NON_K", 0, "inf", f"Group #{g:02d}: leaves K at step <=366 and never returns in 20M steps")
        elif g in {23, 24, 29, 32, 36}:
            verdicts[m] = ("OTHER_D", "SYRACUSE_2ADIC", 0, "2-adic Collatz (max f_4/round)", f"Group #{g:02d}: 2-adic Syracuse decrement k=v2(3a+c)+1 over 10^41000-digit counter")
        else:
            raise ValueError(f"Unhandled group {g} for {m}")

assert len(verdicts) == 866, f"Expected 866 verdicts, got {len(verdicts)}"

tsv_path = os.path.join(WORKDIR, "rescued_866_verdicts.tsv")
with open(tsv_path, "w", encoding="utf-8") as f:
    f.write("idx\ttag\tslot\tmachine\td_cat\tverdict\thalt_round\tscale\tdetail\n")
    for r in rows:
        if r["in_cls53"]:
            continue
        d_cat, v, rnd, scale, detail = verdicts[r["m"]]
        f.write(f"{r['idx']}\t{r['tag']}\t{r['slot']}\t{r['m']}\t{d_cat}\t{v}\t{rnd}\t{scale}\t{detail}\n")

print(f"Successfully wrote {len(verdicts)} rows to rescued_866_verdicts.tsv!")
summary = collections.Counter((v[0], v[1], v[2] if v[1].startswith("HALT") else 0) for v in verdicts.values())
for k, cnt in sorted(summary.items()):
    print(f"  {k[0]:7s} | {k[1]:18s} | Rnd={k[2]} : {cnt}")
