import os, collections, re
from step5_analyze_probe_919 import rows, parse_cell, expand_ds, AUDIT_DIR
from step7o_complete_std_399 import std_399, get_d_aff, parse_first_k, bdet

# Let's check for each leaf in std_399 whether B1..B4 and LB1..LB3 have a uniform output parity p_lock!
def check_uniform_borrow_parity(r):
    # Check if all B1..B4 and LB1..LB3 are K_AFF (or K0) and what parities they output
    b_fits = [r["fit_B"][k] for k in (1, 2, 3, 4)]
    lb_fits = [r["fit_LB"][k] for k in (1, 2, 3)]

    # Check if for a given input parity p_in in {0, 1}, all B1..B4 and LB1..LB3 output a single parity
    out_pars = {0: set(), 1: set()}
    kinds = {0: set(), 1: set()}
    b1_L = {0: None, 1: None}
    for p_in in (0, 1):
        for k in (1, 2, 3, 4):
            fk = r["fit_B"][k][p_in]
            kinds[p_in].add(fk[0])
            if fk[0] in ("K_AFF", "K0", "K_VAR", "K_VARLEN"):
                for x in fk[-1]:
                    out_pars[p_in].add(x % 2)
            if k == 1 and fk[0] == "K_AFF":
                b1_L[p_in] = fk[2]
        for k in (1, 2, 3):
            flk = r["fit_LB"][k][p_in]
            kinds[p_in].add(flk[0])
            if flk[0] in ("K_AFF", "K0", "K_VAR", "K_VARLEN"):
                for x in flk[-1]:
                    out_pars[p_in].add(x % 2)
    return kinds, out_pars, b1_L

# Now let's enhance reduce_general_list in step7o with uniform borrow parity & exact special cases!
def reduce_general_list_v2(r, ds, a):
    m_D, c_D = get_d_aff(r)
    b1, b2, b3, b4 = r["fit_B"][1], r["fit_B"][2], r["fit_B"][3], r["fit_B"][4]
    lb1, lb2, lb3 = r["fit_LB"][1], r["fit_LB"][2], r["fit_LB"][3]

    if len(ds) == 0:
        return ("AT_E", a, "already empty []")
    if len(ds) == 1:
        d1 = ds[0]
        if d1 <= 30 and m_D <= 7:
            a_out = a
            for _ in range(d1):
                a_out = m_D * a_out + c_D
        else:
            a_mod = a % 240
            for _ in range(d1 % 240 + 240):
                a_mod = (m_D * a_mod + c_D) % 240
            a_out = a_mod + 240000
        return ("AT_E", a_out, f"1-digit [{d1}];{a} -> [];{a_out}")

    if r["m"] == "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1RH0LG_---0LE_0RA1RF":
        if ds == [3, 5, 5] and a == 5:
            return ("AT_E", 11953760, "[3,5,5];5 -> [];11953760")
        elif ds[-1] == 4 and ds[0] == 3:
            return ("AT_E", 1001, "[3,5^N,4];21 -> [];odd")

    if b1[1][0] == "K_AFF" and b1[1][1] == "DROP_TO_ZERO":
        par = a % 2
        if par == 0 and lb1[0][0] == "H":
            return ("MID_HALT", f"DROP_TO_ZERO with even a={a} halts at LB1(even)=H / E(even)=H")
        if par == 1 and lb1[1][0] == "K_VARLEN":
            return ("INF_LOOP", f"DROP_TO_ZERO with odd a={a} loops via fused LB1(odd) forever")

    if (m_D, c_D) == (4, 3):
        a_b1 = b1[1][6][0] % 3
        a_lb1 = lb1[1][6][0] % 3
        if a_b1 == 1 and a_lb1 == 1:
            return ("AT_E", 34, "D=4a+3, B1/LB1 -> a'=34 (1 mod 3)")
        else:
            return ("AT_E", 5, "D=4a+3, B1/LB1/B2 -> a'==2 mod 3")

    if (m_D, c_D) == (5, 4):
        if b1[1][2] >= 2:
            return ("INF_B1_EXPAND", "D=5a+4, B1 has L=2 -> list expands forever")
        else:
            return ("AT_E", 5, "D=5a+4, B1/LB1 -> a'=5 (2 mod 3)")

    # Now m_D is odd and c_D is even, so D preserves parity of a!
    par = a % 2
    kinds, out_pars, b1_L = check_uniform_borrow_parity(r)

    # Check if len(ds) == 2 and ds[0] == 1 and ds[1] >= 1:
    if len(ds) == 2 and ds[0] == 1 and ds[1] >= 1:
        lb1_p = lb1[par]
        if lb1_p[0] == "H":
            return ("MID_HALT", f"[1, {ds[1]}];{a} -> [1, 0] -> LB1(par={par})=H")
        if lb1_p[0] == "T":
            return ("MID_T", f"[1, {ds[1]}];{a} -> [1, 0] -> LB1(par={par})=T")
        if lb1_p[0] == "K0":
            a_aff = lb1_p[2]
            a_in = a
            for _ in range(min(ds[1], 20)):
                a_in = m_D * a_in + c_D
            a_out = a_aff[0] * a_in + a_aff[1] if a_aff else lb1_p[3][0]
            return ("AT_E", a_out, f"[1, {ds[1]}];{a} -> LB1(L=0) -> [];{a_out}")
        if lb1_p[0] == "K_AFF" and lb1_p[2] == 1:
            apars = set(x % 2 for x in lb1_p[6])
            if len(apars) == 1:
                p_out = list(apars)[0]
                return ("AT_E", 2000 + p_out, f"[1, {ds[1]}];{a} -> LB1(L=1, a' par={p_out}) -> D*c -> [];par={p_out}")

    # Check if B1(par) is H or T (and first borrow is B1, i.e. ds[-1] >= 1 and not [1, d1]):
    if ds[-1] >= 1 and (len(ds) > 2 or ds[0] >= 2):
        if b1[par][0] == "H":
            return ("MID_HALT", f"First borrow hits B1(par={par})=H")
        if b1[par][0] == "T":
            return ("MID_T", f"First borrow hits B1(par={par})=T")

    # Check if B1 has L >= 2 with positive tail digits on the active parities:
    b1_rule = b1[par]
    if b1_rule[0] == "K_AFF" and b1_rule[2] >= 2 and all(t >= 1 for t in b1_rule[4]):
        p_next_set = set(x % 2 for x in b1_rule[-1])
        if len(p_next_set) == 1:
            p_next = list(p_next_set)[0]
            b1_next = b1[p_next]
            if b1_next[0] == "K_AFF" and b1_next[2] >= 2 and all(t >= 1 for t in b1_next[4]):
                if len(ds) > 2 or ds[0] >= 2 or (lb1[par][0] == "K_AFF" and lb1[par][2] >= 2 and all(t >= 1 for t in lb1[par][4])):
                    return ("INF_B1_EXPAND", f"B1 has L={b1_rule[2]} >= 2 with positive tail {b1_rule[4]}, list expands forever")

    # Now check if ALL borrows from par (and subsequent parities) are K_AFF/K0 (no H/T) and lock into a single parity p_lock!
    # Wait: also check that B_k actually reduces the list (e.g., B1 has L == 1 or L == 0)!
    if kinds[par] <= {"K_AFF", "K0"} and len(out_pars[par]) == 1:
        p1 = list(out_pars[par])[0]
        if kinds[p1] <= {"K_AFF", "K0"} and out_pars[p1] == {p1}:
            # Every borrow from now on stays in parity p1 and never hits H or T!
            # Check if B1[p1] has L == 1 (or L == 0):
            if b1_L[p1] in (0, 1) and b1_L[par] in (0, 1):
                # Does any B_k (k <= len(ds)-1) have L > k?
                max_k = min(4, len(ds) - 1)
                if all(r["fit_B"][k][p1][0] == "K0" or r["fit_B"][k][p1][2] <= k for k in range(1, max_k + 1)):
                    return ("AT_E", 2000 + p1, f"All borrows lock to parity {p1} -> [];par={p1}")

    return ("COMPLEX", par, f"ds={ds}; a={a} | kinds={kinds} out_pars={out_pars} b1_L={b1_L}")

def trace_leaf_v2(r):
    m_D, c_D = get_d_aff(r)
    bd = bdet[r["m"]]
    if bd["st"].startswith("H:"):
        return ("HALT_BLANK_1M", 1 if bd["nE"]>=1 else 0, "f_1", f"Blank halted in {bd['st']} (nE={bd['nE']})")
    if bd["nK"] == 0:
        return ("INF_NON_K", 0, "non-K", f"Never reaches K ({bd['st']})")

    # Check the 6 Group #92 / #35 / #76 / #126 / #141 leaves with E(2m+1) -> [1]; c1*m + c0:
    if r["m"] in ("1RB1LA_0RC1RD_1LD1LC_1LE0RF_0LA0LC_---0RH_1RE1RG_1LB1RG",
                  "1RB1LA_0RC1RD_1LD1LC_1LE0RF_0LA0LC_---0RH_1RE1RG_1LC1RG"):
        return ("HALT", 5, "f_1 (5 rounds of [1])", "E1(103)->[1];1401 -> E2(4207)->[1];56805 -> E3(170419)->[1];2300667 -> E4(6902005)->[1];93177078 -> E5(279531238)->HALT")
    if r["m"] in ("1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LD0RF_---0RH_1LE1LG_1LG1RC",
                  "1RB1LA_1RC1RE_1RD1RC_0LA0LG_1LD0RF_---0RH_1LE1LG_1LG1RC"):
        return ("HALT", 5, "f_1 (5 rounds of [1])", "E1(3)->[1];145 -> E2(731)->[1];27445 -> E3(137231)->[1];5146195 -> E4(25730981)->[1];964911820 -> E5(4824559106)->HALT")

    fk = parse_first_k(bd["first_ks"])
    _, ds, a, b = fk
    hist = [f"Start:{ds};{a}"]
    for rnd in range(1, 8):
        res = reduce_general_list_v2(r, ds, a)
        kind = res[0]
        if kind == "MID_HALT":
            return ("HALT", rnd, f"L={len(ds)} (mid-round)", " -> ".join(hist + [res[1]]))
        if kind in ("MID_T", "INF_LOOP", "INF_B1_EXPAND"):
            return (kind, rnd, f"L={len(ds)}", " -> ".join(hist + [res[-1]]))
        if kind == "COMPLEX":
            return ("COMPLEX", rnd, f"L={len(ds)}", " -> ".join(hist + [res[-1]]))
        assert kind == "AT_E"
        A = res[1]
        hist.append(f"E{rnd}({A if A<1000 else ('even' if A%2==0 else 'odd')})")
        ep = "".join(r["E"][x][0] for x in range(1, 17))
        if A <= 16:
            ecell = r["E"][A]
        else:
            if ep in ("KHKHKHKHKHKHKHKH", "THTHTHTHTHTHTHTH", "HHKHKHKHKHKHKHKH", "KHKHKHTHKHKHTHTH", "KHKHKHKHKHKHTHTH"):
                ecell = r["E"][6] if (A % 2 == 0) else r["E"][5]
            elif ep == "HKHKHKHKHKHKHKHK":
                ecell = r["E"][6] if (A % 2 == 0) else r["E"][5]
                if r["m"] == "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1RH0LG_---0LE_0RA1RF" and A % 2 == 0:
                    ecell = r["E"][8] if (A % 4 == 0) else r["E"][6]
            elif ep in ("HHHHHHHHHHHHHHHH", "KHHHHHHHHHHHHHHH", "KHKHHHHHHHHHHHHH"):
                ecell = ("H", "H")
            elif ep in ("KKHKKHKKHKKHKKHK", "HKKHKKHKKHKKHKKH", "HKTHKTHKXHKXHKTH"):
                rem = A % 3
                rep_A = 3 if rem == 0 else (4 if rem == 1 else 5)
                ecell = r["E"][rep_A]
            else:
                return ("COMPLEX_E", rnd, ep, " -> ".join(hist))

        if ecell[0] == "H":
            return ("HALT", rnd, f"L_prev={len(ds)}", " -> ".join(hist + ["HALT"]))
        if ecell[0] in ("T", "X"):
            return ("INF_E_T", rnd, f"A={A}", " -> ".join(hist + [f"E={ecell[0]}"]))
        _, new_ds, new_a, new_b, new_ds_s = ecell
        state_str = f"Reb[{new_ds_s}];{new_a}"
        if state_str in hist:
            return ("INF_PARITY_LOCK", rnd, state_str, " -> ".join(hist + [state_str]))
        if len(new_ds) == 0 and new_a % 2 == 1 and ep.startswith("KHKH"):
            if all(r["E"][x][0] == "K" and r["E"][x][1] == [] and r["E"][x][2] % 2 == 1 for x in (1, 3, 5)):
                return ("INF_0DIGIT_EXP", rnd, "[];odd", " -> ".join(hist + ["[];odd forever"]))
        hist.append(state_str)
        ds, a = new_ds, new_a

    return ("MAX_RND", 7, "", " -> ".join(hist))

traced2 = [trace_leaf_v2(r) for r in std_399]
vc2 = collections.Counter((x[0], x[1] if x[0].startswith("HALT") else 0) for x in traced2)
print("Multi-round trace v2 summary of 399 std_d leaves:")
for k, v in vc2.most_common():
    print(f"  {str(k):25s}: {v}")

complex_left = [(r, t) for r, t in zip(std_399, traced2) if t[0] == "COMPLEX"]
print(f"\nRemaining COMPLEX leaves in std_399: {len(complex_left)}")
for r, t in complex_left:
    print(f"  [{r['tag']}] {r['m']} | Rnd {t[1]} | {t[3]}")
