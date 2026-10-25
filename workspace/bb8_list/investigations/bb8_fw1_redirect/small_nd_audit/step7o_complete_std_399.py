import os, collections, re
from step5_analyze_probe_919 import rows, parse_cell, expand_ds, AUDIT_DIR
from step7n_eval_all_399 import std_399, results, get_d_aff, parse_first_k, bdet

# Let's inspect all leaves in std_399 by how their borrows B1..B4 and LB1..LB3 behave!
# Specifically, for each leaf r, let's trace Round 1, Round 2, Round 3, Round 4!

def analyze_e_map(r):
    # Return dict of A -> (kind, ds, a_out) for A in 1..16
    return r["E"]

# Let's check for any list (ds, a) with len(ds) >= 2 on a machine r in std_399:
# Can we determine the exact parity (or value) of A_out when (ds, a) reduces to []; A_out,
# OR whether it hits H / T / INF_B1_EXPAND during the reduction?
def reduce_general_list(r, ds, a):
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

    # Special cases already handled:
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
    # Check how many trailing zeros ds currently has:
    k0 = 0
    for x in reversed(ds):
        if x == 0: k0 += 1
        else: break

    # If k0 == 0, D reduces ds[-1] -> 0 while preserving par = a % 2, so the first borrow is at k = 1!
    # Wait: what if ds has 2 digits [d2, d1] with d1 >= 1?
    # Let's check the borrow rules B1..B4 and LB1..LB3!
    # Suppose for BOTH parities (or for the parity that B_k/LB_k maps into),
    # all active borrows B1..B4 and LB1..LB3 output the SAME parity p_lock!
    # Let's check if B1, B2, B3, B4, LB1, LB2, LB3 all output a single parity p_lock (and never H/T, and B1 has L == 1)!
    b1_p = b1[par]
    if b1_p[0] == "H":
        return ("MID_HALT", f"Hits B1(par={par})=H")
    if b1_p[0] == "T":
        return ("MID_T", f"Hits B1(par={par})=T")

    # What if len(ds) == 2 and ds[0] == 1 and ds[1] >= 1?
    # Then the ONLY borrow is LB1(par)!
    if len(ds) == 2 and ds[0] == 1 and ds[1] >= 1:
        lb1_p = lb1[par]
        if lb1_p[0] == "H":
            return ("MID_HALT", f"[1, {ds[1]}];{a} -> [1, 0] -> LB1(par={par})=H")
        if lb1_p[0] == "T":
            return ("MID_T", f"[1, {ds[1]}];{a} -> [1, 0] -> LB1(par={par})=T")
        if lb1_p[0] == "K0":
            # LB1([1, 0], a) -> []; a_out!
            a_aff = lb1_p[2]
            # After ds[1] D-steps, a_in = D^{ds[1]}(a)
            a_in = a
            for _ in range(min(ds[1], 20)):
                a_in = m_D * a_in + c_D
            a_out = a_aff[0] * a_in + a_aff[1] if a_aff else lb1_p[3][0]
            return ("AT_E", a_out, f"[1, {ds[1]}];{a} -> LB1(L=0) -> [];{a_out}")
        if lb1_p[0] == "K_AFF" and lb1_p[2] == 1:
            # LB1([1, 0], a) -> [c(a_in)]; a_out (1-digit list!)
            a_out_sample = lb1_p[6][0]
            # Wait: is parity of a_out constant in lb1_p?
            apars = set(x % 2 for x in lb1_p[6])
            if len(apars) == 1:
                p_out = list(apars)[0]
                # 1-digit list [c]; a_out reduces via D to []; A_next with parity p_out!
                return ("AT_E", 2000 + p_out, f"[1, {ds[1]}];{a} -> LB1(L=1, a' par={p_out}) -> D*c -> [];par={p_out}")

    return ("COMPLEX", par, f"ds={ds}; a={a}")

# Let's test this on all 399 leaves across up to 6 rounds!
def trace_leaf_rounds(r):
    m_D, c_D = get_d_aff(r)
    bd = bdet[r["m"]]
    if bd["st"].startswith("H:"):
        return ("HALT", 1 if bd["nE"]>=1 else 0, "f_1", f"Blank halted in {bd['st']} (nE={bd['nE']})")
    if bd["nK"] == 0:
        return ("INF_NON_K", 0, "non-K", f"Never reaches K ({bd['st']})")

    fk = parse_first_k(bd["first_ks"])
    _, ds, a, b = fk
    hist = [f"Start: {ds};{a}"]
    for rnd in range(1, 8):
        res = reduce_general_list(r, ds, a)
        kind = res[0]
        if kind == "MID_HALT":
            return ("HALT", rnd, f"L={len(ds)}", " -> ".join(hist + [res[1]]))
        if kind in ("MID_T", "INF_LOOP", "INF_B1_EXPAND"):
            return (kind, rnd, f"L={len(ds)}", " -> ".join(hist + [res[-1]]))
        if kind == "COMPLEX":
            return ("COMPLEX", rnd, f"L={len(ds)}", " -> ".join(hist + [res[-1]]))
        assert kind == "AT_E"
        A = res[1]
        hist.append(f"E{rnd}({A if A<1000 else ('even' if A%2==0 else 'odd')})")
        # Now evaluate E(A)!
        # Check r["E"] pattern:
        ep = "".join(r["E"][x][0] for x in range(1, 17))
        if A <= 16:
            ecell = r["E"][A]
        else:
            # Determine which residue class A belongs to:
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
            return ("HALT", rnd, f"A={A}", " -> ".join(hist + ["HALT"]))
        if ecell[0] in ("T", "X"):
            # Wait: check if ecell[0] == "T" is one of the 4 machines where E(odd) builds [1]; 37A+33!
            if ep in ("KHKHKHTHKHKHTHTH", "KHKHKHKHKHKHTHTH") and A % 2 == 1:
                ecell = r["E"][5]
            else:
                return ("INF_E_T", rnd, f"A={A}", " -> ".join(hist + [f"E={ecell[0]}"]))
        # Rebuild!
        _, new_ds, new_a, new_b, new_ds_s = ecell
        # Check if we are in a repeating cycle of (new_ds, new_a):
        state_str = f"Reb[{new_ds_s}];{new_a}"
        if state_str in hist:
            return ("INF_CYCLE", rnd, state_str, " -> ".join(hist + [state_str]))
        # Also check if E(odd) always builds [1]; odd and D preserves odd:
        if len(new_ds) == 1 and new_a % 2 == 1 and (m_D % 2 == 1 and c_D % 2 == 0) and ep.startswith("KHKH"):
            # Check if E(1), E(3), E(5) all build [1]; odd:
            if all(r["E"][x][0] == "K" and r["E"][x][1] == [1] and r["E"][x][2] % 2 == 1 for x in (1, 3, 5)):
                return ("INF_1DIGIT_EXP", rnd, "[1];odd", " -> ".join(hist + ["[1];odd forever"]))
        if len(new_ds) == 0 and new_a % 2 == 1 and ep.startswith("KHKH"):
            if all(r["E"][x][0] == "K" and r["E"][x][1] == [] and r["E"][x][2] % 2 == 1 for x in (1, 3, 5)):
                return ("INF_0DIGIT_EXP", rnd, "[];odd", " -> ".join(hist + ["[];odd forever"]))
        hist.append(state_str)
        ds, a = new_ds, new_a

    return ("MAX_RND", 7, "", " -> ".join(hist))

traced = [trace_leaf_rounds(r) for r in std_399]
vc = collections.Counter((x[0], x[1] if x[0]=="HALT" else 0) for x in traced)
print("Multi-round trace summary of 399 std_d leaves:")
for k, v in vc.most_common():
    print(f"  {str(k):25s}: {v}")

# Print all HALT leaves with rnd >= 2!
print("\n--- HALT leaves with rnd >= 2 so far ---")
for r, t in zip(std_399, traced):
    if t[0] == "HALT" and t[1] >= 2:
        print(f"  [{r['tag']}] {r['m']} | Rnd {t[1]} | {t[3]}")
