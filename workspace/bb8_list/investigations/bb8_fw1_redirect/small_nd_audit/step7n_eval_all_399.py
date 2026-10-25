import os, collections, re
from step5_analyze_probe_919 import rows, parse_cell, expand_ds, AUDIT_DIR
from step7j_analyze_groups_399 import std_399, fit_borrow_table, bdet

# Let's classify all 399 std_d leaves systematically!
# For each leaf r in std_399, let's check:
# 1. D rule: (m_D, c_D)
# 2. E(1..16) rule
# 3. B1..B4 and LB1..LB3 fitted rules
# 4. Blank-tape startup from bdet[r['m']]

def get_d_aff(r):
    a_outs = [x[2] for x in r["D"]]
    m = a_outs[1] - a_outs[0]
    c = a_outs[0] - m * 1
    return m, c

def parse_first_k(ks):
    if not ks:
        return None
    first = ks.split(" -> ")[0].strip()
    m = re.match(r"^@(\d+):\[([^\]]*)\];(-?\d+);(-?\d+)$", first)
    if not m:
        return None
    return int(m.group(1)), expand_ds(m.group(2)), int(m.group(3)), int(m.group(4))

# Let's analyze what happens in a round starting from (ds, a) for any std_399 leaf!
# Wait: let's inspect the exact combination of (m_D, c_D, ep, B1..B4, LB1..LB3, start_ds, start_a)
# across all 399 leaves.
results = []
for idx, r in enumerate(std_399):
    m_D, c_D = get_d_aff(r)
    bd = bdet[r["m"]]
    ep = "".join(r["E"][a][0] for a in range(1, 17))
    fk = parse_first_k(bd["first_ks"])
    b1 = r["fit_B"][1]
    b2 = r["fit_B"][2]
    b3 = r["fit_B"][3]
    b4 = r["fit_B"][4]
    lb1 = r["fit_LB"][1]
    lb2 = r["fit_LB"][2]
    lb3 = r["fit_LB"][3]

    # Case 0: Blank tape already halted in 1M steps or never reached K
    if bd["st"].startswith("H:"):
        results.append((r, "HALT_BLANK_1M", 1 if bd["nE"]>=1 else 0, f"Blank halted at {bd['st']} (nE={bd['nE']}, maxL={bd['maxlen']})"))
        continue
    if bd["nK"] == 0:
        results.append((r, "INF_NON_K", 0, f"Never reaches K on blank tape ({bd['st']})"))
        continue

    # Check if E(1..16) is THTHTHTH... (where E(odd) = T non-halting, E(even) = H)
    # Wait: let's handle general round reduction from fk = (step0, ds0, a0, b0)
    step0, ds0, a0, b0 = fk

    # Helper to determine the outcome of reducing a non-empty list (ds, a) to E(A_next) or mid-round H/T/INF
    def reduce_list(ds, a):
        if len(ds) == 0:
            return ("AT_E", a, "len=0")
        if len(ds) == 1:
            d1 = ds[0]
            # Apply D d1 times:
            if m_D == 1:
                a_out = a + d1 * c_D
            else:
                # For small d1 (<= 20), compute exact a_out; for large d1, compute mod 12 and approximate size
                if d1 <= 30:
                    a_out = a
                    for _ in range(d1):
                        a_out = m_D * a_out + c_D
                else:
                    # mod 24 is enough for mod 2, mod 3, mod 4, mod 8
                    a_mod = a % 240
                    for _ in range(d1 % 240 + 240):
                        a_mod = (m_D * a_mod + c_D) % 240
                    a_out = a_mod + 240 * 1000
            return ("AT_E", a_out, f"1-digit [{d1}] -> A={a_out}")

        # Now len(ds) >= 2!
        # Check Special Case A: m == 1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1RH0LG_---0LE_0RA1RF (already solved!)
        if r["m"] == "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1RH0LG_---0LE_0RA1RF":
            if ds == [3, 5, 5] and a == 5:
                return ("AT_E", 11953760, "[3,5,5];5 -> A=11953760 (0 mod 4)")
            elif ds[-1] == 4 and ds[0] == 3:
                return ("AT_E", 1001, "[3,5^N,4];21 -> A odd")

        # Check Special Case B: DROP_TO_ZERO B1 on (m_D, c_D) = (5, 6) or (3, 4) where D preserves parity:
        if b1[1][0] == "K_AFF" and b1[1][1] == "DROP_TO_ZERO":
            # In all these 33 machines, D preserves parity, B1 preserves parity.
            # Look at ds:
            par = a % 2
            if par == 0 and lb1[0][0] == "H":
                # Check if [1, 0] is reached or [d_n, ...] reduces to LB1(even)=H or E(even)=H!
                return ("MID_HALT", f"Even parity a={a} with DROP_TO_ZERO reaches LB1(even)=H / E(even)=H")
            if par == 1 and lb1[1][0] == "K_VARLEN":
                # Starts with odd a! If ds = [1, 4], 4 D-steps give [1, 0]; a_odd -> LB1(odd) fused rebuild [1, 5^N, 4]; 33 (odd), which loops forever inLB1(odd)!
                # What if ds = [1, 5, 5]; 5? 5 D-steps give [1, 5, 0] -> B1 gives [1, 3] -> 3 D-steps give [1, 0]; a_odd -> LB1(odd) fused rebuild forever!
                return ("INF_LOOP", "Odd parity with DROP_TO_ZERO B1 and fused LB1(odd) rebuilds [1,5^N,...] (odd) forever")

        # Now standard borrow prefix [2, 1]:
        # Let's check what happens when reducing the rightmost digit d_1 to 0 via D:
        # In one D-chain of length d_1 >= 1:
        # If m_D is odd and c_D is even, parity of a is preserved by D!
        # What if m_D == 4 and c_D == 3? Then a_after_D is ALWAYS ODD, and a_after_D == a (mod 3)!
        # What if m_D == 5 and c_D == 4? Then for a == 2 (mod 3), 5a+4 == 2 (mod 3) is preserved!
        if (m_D, c_D) == (4, 3):
            # Mod-3 gate: E(A) = H iff A == 1 (mod 3).
            # Check a_out mod 3 of B1, LB1:
            a_b1 = b1[1][6][0] % 3
            a_lb1 = lb1[1][6][0] % 3
            if a_b1 == 1 and a_lb1 == 1:
                return ("AT_E", 34, "D=4a+3 preserves mod 3; B1/LB1 set a'=34 (1 mod 3) -> E(1 mod 3)=H")
            else:
                return ("AT_E", 5, "D=4a+3 preserves mod 3; B1/LB1/B2 set a'==2 mod 3 -> E(2 mod 3)=K forever")

        if (m_D, c_D) == (5, 4):
            # 8 leaves in [d, e, g]: we already proved 4 have B1/LB1 L=2 -> INF_B1_EXPAND, and 4 have B1/LB1 L=1 with a'=5 (2 mod 3) fixed point of 5a+4 mod 3!
            if b1[1][2] >= 2:
                return ("INF_B1_EXPAND", "B1 has L=2 ([2,1,c,3];1), expanding list length by +1 every borrow forever")
            else:
                return ("AT_E", 5, "B1/LB1 set a'=5 (2 mod 3), invariant under D=5a+4 -> E(2 mod 3)=K forever")

        # Now for all remaining leaves, m_D is ODD and c_D is EVEN, so D preserves parity of a!
        par = a % 2
        # Check if B1(par) is H or T:
        if b1[par][0] == "H":
            return ("MID_HALT", f"Hits B1(par={par})=H during list reduction")
        if b1[par][0] == "T":
            return ("MID_T", f"Hits B1(par={par})=T (non-halting) during list reduction")

        # Check if B1(par) has L >= 2 with positive tail digits (B1 list-expansion trap!):
        # Wait: what if ds is [d_2, 0] (so it immediately hits B1 or LB1)? Even then, if B1/LB1 has L >= 2 with positive tail digits, it expands!
        # Wait: what if LB1(par) is H and ds is [1, d_1] (length 2 with leftmost digit 1)?
        if len(ds) == 2 and ds[0] == 1 and ds[1] >= 1:
            # 1-step D-chain reduces [1, d_1] to [1, 0], which immediately calls LB1(par)!
            if lb1[par][0] == "H":
                return ("MID_HALT", f"[1, {ds[1]}] reduces via D to [1, 0] and hits LB1(par={par})=H")
            if lb1[par][0] == "T":
                return ("MID_T", f"[1, {ds[1]}] reduces via D to [1, 0] and hits LB1(par={par})=T")

        # Check if ALL borrows B1..B4 and LB1..LB3 on both parities (or on invariant parity) preserve or force a specific parity!
        # Let's check the output parities of B1, B2, B3, LB1, LB2, LB3:
        b1_rule = b1[par]
        # Wait: does B1(par) output a constant parity of a_out?
        b1_apar = set(x % 2 for x in b1_rule[-1])
        if len(b1_apar) == 1:
            p_after_b1 = list(b1_apar)[0]
        else:
            p_after_b1 = None

        # Check if B1 has L >= 2 with all tail digits >= 1:
        if b1_rule[0] == "K_AFF" and b1_rule[2] >= 2 and all(t >= 1 for t in b1_rule[4]):
            # Wait: what if p_after_b1 != par and b1[p_after_b1] has L == 1 or H?
            b1_next = b1[p_after_b1] if p_after_b1 is not None else None
            if b1_next and b1_next[0] == "K_AFF" and b1_next[2] >= 2 and all(t >= 1 for t in b1_next[4]):
                # Every B1 borrow (and LB1 borrow if reached first) has tail digits >= 1 and L >= 2!
                # Wait: what if ds is [1, d_1] so it hits LB1(par) first?
                lb1_rule = lb1[par]
                if lb1_rule[0] == "K_AFF" and lb1_rule[2] >= 2 and all(t >= 1 for t in lb1_rule[4]):
                    return ("INF_B1_EXPAND", f"B1/LB1 has L={b1_rule[2]} >= 2 with positive tail {b1_rule[4]}, list length grows forever")
                elif len(ds) > 2 or ds[0] >= 2:
                    return ("INF_B1_EXPAND", f"B1 has L={b1_rule[2]} >= 2 with positive tail {b1_rule[4]}, list length grows forever")

        return ("NEED_TRACE", par, f"ds={ds}; a={a}")

    results.append((r, "TRACE", 0, reduce_list(ds0, a0)))

# Let's see how many of the 399 leaves are already resolved vs NEED_TRACE or AT_E!
cnts = collections.Counter(x[1] if x[1] != "TRACE" else x[3][0] for x in results)
print("First-pass reduction summary of 399 std_d leaves:")
for k, v in cnts.most_common():
    print(f"  {k:20s}: {v}")
