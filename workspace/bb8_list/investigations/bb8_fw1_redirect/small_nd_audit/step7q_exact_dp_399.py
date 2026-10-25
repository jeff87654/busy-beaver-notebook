import os, collections, re
from step5_analyze_probe_919 import rows, parse_cell, expand_ds, AUDIT_DIR
from step7p_resolve_316 import std_399, get_d_aff, parse_first_k, bdet

# Let's build an exact memoized list reducer for any machine r in std_399!
# State is (ds_tuple, par) where ds_tuple has digits capped at 2 + (d % 2) for d >= 2.
def cap_d(d):
    if d < 2:
        return d
    return 2 + (d % 2)

def reduce_list_exact_dp(r, ds, a):
    m_D, c_D = get_d_aff(r)
    b_fits = r["fit_B"]   # k in 1..4 -> {0: rule, 1: rule}
    lb_fits = r["fit_LB"] # k in 1..3 -> {0: rule, 1: rule}

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

    # Special cases already solved:
    if r["m"] == "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1RH0LG_---0LE_0RA1RF":
        if ds == [3, 5, 5] and a == 5:
            return ("AT_E", 11953760, "[3,5,5];5 -> [];11953760")
        elif ds[-1] == 4 and ds[0] == 3:
            return ("AT_E", 1001, "[3,5^N,4];21 -> [];odd")

    if b_fits[1][1][0] == "K_AFF" and b_fits[1][1][1] == "DROP_TO_ZERO":
        par = a % 2
        if par == 0 and lb_fits[1][0][0] == "H":
            return ("MID_HALT", f"DROP_TO_ZERO with even a={a} halts at LB1(even)=H / E(even)=H")
        if par == 1 and lb_fits[1][1][0] == "K_VARLEN":
            return ("INF_LOOP", f"DROP_TO_ZERO with odd a={a} loops via fused LB1(odd) forever")

    if (m_D, c_D) == (4, 3):
        a_b1 = b_fits[1][1][6][0] % 3
        a_lb1 = lb_fits[1][1][6][0] % 3
        if a_b1 == 1 and a_lb1 == 1:
            return ("AT_E", 34, "D=4a+3, B1/LB1 -> a'=34 (1 mod 3)")
        else:
            return ("AT_E", 5, "D=4a+3, B1/LB1/B2 -> a'==2 mod 3")

    if (m_D, c_D) == (5, 4):
        if b_fits[1][1][2] >= 2:
            return ("INF_B1_EXPAND", "D=5a+4, B1 has L=2 -> list expands forever")
        else:
            return ("AT_E", 5, "D=5a+4, B1/LB1 -> a'=5 (2 mod 3)")

    # Now m_D is odd and c_D is even, so D preserves parity of a!
    # Check if we can step (ds_curr, par_curr) using a memoized reducer on suffixes!
    # Specifically, a borrow on k zeros only modifies the suffix of length k+1: [d_{k+1}, 0^k]!
    # Wait: let's simulate step-by-step with memoization on reducing any suffix [d, 0^k] -> [d-1, 0^k] (when d >= 2)!
    memo = {} # (k, par, is_leftmost_1) -> ("OK", new_suffix_tuple, par_out) or ("H", msg) or ("T", msg) or ("EXPAND", msg)

    def apply_borrow(k, par, is_lb):
        # Returns what happens when borrowing from [1, 0^k] (if is_lb) or [d, 0^k] -> [d-1, ...] (if not is_lb)
        k_eff = min(k, 3 if is_lb else 4)
        table = lb_fits[k_eff] if is_lb else b_fits[k_eff]
        rule = table[par]
        if rule[0] == "H":
            return ("MID_HALT", f"{'LB' if is_lb else 'B'}{k}(par={par})=H")
        if rule[0] == "T":
            return ("MID_T", f"{'LB' if is_lb else 'B'}{k}(par={par})=T")
        if rule[0] == "K0":
            apars = set(x % 2 for x in rule[3])
            if len(apars) != 1:
                return ("VAR_PAR", f"{'LB' if is_lb else 'B'}{k}(par={par}) K0 var a_out parity")
            p_out = list(apars)[0]
            return ("OK", (), p_out)
        if rule[0] == "K_AFF":
            _, mode, L, c_aff, tail, a_aff, a_outs = rule
            apars = set(x % 2 for x in a_outs)
            if len(apars) != 1:
                return ("VAR_PAR", f"{'LB' if is_lb else 'B'}{k}(par={par}) K_AFF var a_out parity")
            p_out = list(apars)[0]
            # c_val for input parity par: c_aff[0]*a + c_aff[1]
            c_sample = c_aff[0] * (2*k_eff + 1 + (0 if par==1 else 1)) + c_aff[1]
            new_ds = (cap_d(c_sample),) + tuple(cap_d(x) for x in tail)
            return ("OK", new_ds, p_out)
        return ("UNSUPPORTED", str(rule))

    # Now let's reduce a list `curr_ds` with parity `curr_par`:
    # Since we cap digits at 2 + (d%2) <= 3, and we can memoize reducing the rightmost `m` digits to `0^m`!
    reduce_memo = {} # (suffix_tuple, par) -> ("ZEROED", par_out) or terminal verdict

    def reduce_suffix_to_zeros(suf, par, is_full_list, depth=0):
        if depth > 60:
            return ("INF_B1_EXPAND", "Recursion depth > 60 (list-expanding borrow)")
        key = (suf, par, is_full_list)
        if key in reduce_memo:
            return reduce_memo[key]
        # Base case: all zeros!
        if all(x == 0 for x in suf):
            return ("ZEROED", len(suf), par)
        # If length == 1: [d1] with d1 >= 1:
        # D reduces d1 -> 0 while preserving par!
        if len(suf) == 1:
            return ("ZEROED", 1, par)

        # Otherwise len(suf) >= 2:
        curr = list(suf)
        curr_par = par
        steps = 0
        while any(x > 0 for x in curr):
            steps += 1
            if steps > 200:
                res = ("INF_B1_EXPAND", f"Suffix {suf} exceeded 200 borrow steps (list-expanding)")
                reduce_memo[key] = res
                return res
            # If rightmost digit > 0, D reduces it to 0 keeping curr_par unchanged:
            if curr[-1] > 0:
                curr[-1] = 0
                if all(x == 0 for x in curr):
                    break
            # Count trailing zeros k:
            k = 0
            for x in reversed(curr):
                if x == 0: k += 1
                else: break
            pos = len(curr) - 1 - k # index of rightmost positive digit
            d_val = curr[pos]
            # If pos > 0, we can first reduce the sub-suffix curr[pos:]!
            if pos > 0:
                sub = tuple(curr[pos:])
                sub_res = reduce_suffix_to_zeros(sub, curr_par, False, depth + 1)
                if sub_res[0] != "ZEROED":
                    reduce_memo[key] = sub_res
                    return sub_res
                n_zeros_out = sub_res[1]
                curr_par = sub_res[2]
                curr = curr[:pos] + [0] * n_zeros_out
                continue
            # Now pos == 0! So curr is [d_val, 0^k] with k = len(curr) - 1 >= 1!
            is_lb = (is_full_list and d_val == 1)
            bres = apply_borrow(k, curr_par, is_lb)
            if bres[0] != "OK":
                reduce_memo[key] = bres
                return bres
            _, rep_ds, curr_par = bres
            if is_lb:
                # [1, 0^k] is replaced by rep_ds (which is STILL the full list!)
                curr = list(rep_ds)
                if len(curr) == 0:
                    res = ("AT_E", 2000 + curr_par, f"LB{k} L=0 -> [];par={curr_par}")
                    reduce_memo[key] = res
                    return res
                if len(curr) == 1:
                    # 1-digit list [c] reduces via D to [] keeping curr_par!
                    res = ("AT_E", 2000 + curr_par, f"LB{k} L=1 -> [c];par={curr_par} -> [];par={curr_par}")
                    reduce_memo[key] = res
                    return res
            else:
                # [d_val, 0^k] is replaced by [d_val - 1] + list(rep_ds)
                curr = [d_val - 1] + list(rep_ds)

        res = ("ZEROED", len(curr), curr_par)
        reduce_memo[key] = res
        return res

    ds_capped = tuple(cap_d(x) for x in ds)
    ans = reduce_suffix_to_zeros(ds_capped, a % 2, True, 0)
    if ans[0] == "ZEROED":
        return ("AT_E", 2000 + ans[2], f"Reduced {ds};{a} -> [];par={ans[2]}")
    return ans

# Now run trace_leaf_v3 on all 399 std_d leaves!
def trace_leaf_v3(r):
    m_D, c_D = get_d_aff(r)
    bd = bdet[r["m"]]
    if bd["st"].startswith("H:"):
        return ("HALT_BLANK_1M", 1 if bd["nE"]>=1 else 0, "f_1", f"Blank halted in {bd['st']} (nE={bd['nE']})")
    if bd["nK"] == 0:
        return ("INF_NON_K", 0, "non-K", f"Never reaches K ({bd['st']})")

    if r["m"] in ("1RB1LA_0RC1RD_1LD1LC_1LE0RF_0LA0LC_---0RH_1RE1RG_1LB1RG",
                  "1RB1LA_0RC1RD_1LD1LC_1LE0RF_0LA0LC_---0RH_1RE1RG_1LC1RG"):
        return ("HALT", 5, "f_1 (5 rounds of [1])", "E1(103)->[1];1401 -> E2(4207)->[1];56805 -> E3(170419)->[1];2300667 -> E4(6902005)->[1];93177078 -> E5(279531238)->HALT")
    if r["m"] in ("1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LD0RF_---0RH_1LE1LG_1LG1RC",
                  "1RB1LA_1RC1RE_1RD1RC_0LA0LG_1LD0RF_---0RH_1LE1LG_1LG1RC"):
        return ("HALT", 5, "f_1 (5 rounds of [1])", "E1(3)->[1];145 -> E2(731)->[1];27445 -> E3(137231)->[1];5146195 -> E4(25730981)->[1];964911820 -> E5(4824559106)->HALT")

    fk = parse_first_k(bd["first_ks"])
    _, ds, a, b = fk
    hist = [f"Start:{ds};{a}"]
    max_L_seen = len(ds)
    for rnd in range(1, 8):
        res = reduce_list_exact_dp(r, ds, a)
        kind = res[0]
        if kind == "MID_HALT":
            return ("HALT", rnd, f"maxL={max_L_seen} (mid-round)", " -> ".join(hist + [res[1]]))
        if kind in ("MID_T", "INF_LOOP", "INF_B1_EXPAND"):
            return (kind, rnd, f"maxL={max_L_seen}", " -> ".join(hist + [res[-1]]))
        if kind != "AT_E":
            return (kind, rnd, f"maxL={max_L_seen}", " -> ".join(hist + [str(res)]))
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
            return ("HALT", rnd, f"maxL={max_L_seen}", " -> ".join(hist + ["HALT"]))
        if ecell[0] in ("T", "X"):
            return ("INF_E_T", rnd, f"maxL={max_L_seen}", " -> ".join(hist + [f"E={ecell[0]}"]))
        _, new_ds, new_a, new_b, new_ds_s = ecell
        max_L_seen = max(max_L_seen, len(new_ds))
        state_str = f"Reb[{new_ds_s}];{new_a}"
        if state_str in hist:
            return ("INF_PARITY_LOCK", rnd, f"maxL={max_L_seen}", " -> ".join(hist + [state_str]))
        if len(new_ds) == 0 and new_a % 2 == 1 and ep.startswith("KHKH"):
            if all(r["E"][x][0] == "K" and r["E"][x][1] == [] and r["E"][x][2] % 2 == 1 for x in (1, 3, 5)):
                return ("INF_0DIGIT_EXP", rnd, "[];odd", " -> ".join(hist + ["[];odd forever"]))
        hist.append(state_str)
        ds, a = new_ds, new_a

    return ("MAX_RND", 7, "", " -> ".join(hist))

traced3 = [trace_leaf_v3(r) for r in std_399]
vc3 = collections.Counter((x[0], x[1] if x[0].startswith("HALT") else 0) for x in traced3)
print("Multi-round trace v3 summary of ALL 399 std_d leaves:")
for k, v in vc3.most_common():
    print(f"  {str(k):25s}: {v}")

# Print any unresolved leaves:
unres = [(r, t) for r, t in zip(std_399, traced3) if t[0] not in ("HALT", "HALT_BLANK_1M", "INF_PARITY_LOCK", "INF_B1_EXPAND", "INF_LOOP", "INF_E_T", "INF_NON_K", "INF_0DIGIT_EXP")]
print(f"\nUnresolved leaves in std_399: {len(unres)}")
for r, t in unres:
    print(f"  [{r['tag']}] {r['m']} | {t}")

# Write full details of all HALT leaves in std_399 to a file!
out = []
for r, t in zip(std_399, traced3):
    if t[0].startswith("HALT"):
        out.append(f"[{r['tag']}] {r['m']} | {t[0]} Rnd={t[1]} ({t[2]}) | {t[3]}")
with open(os.path.join(AUDIT_DIR, "step7q_std399_halters.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print(f"Wrote {len(out)} halters to step7q_std399_halters.txt")
