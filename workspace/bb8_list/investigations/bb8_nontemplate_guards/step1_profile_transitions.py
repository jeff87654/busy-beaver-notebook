import os, json

M8_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_m8sweep"
xc = json.load(open(os.path.join(M8_DIR, "xcands.json")))
xc_map = {r["m"]: r for r in xc}

def parse_tm(m):
    rows = m.split("_")
    T = {}
    for q, r in enumerate(rows):
        for s in (0, 1):
            t = r[3*s:3*s+3]
            slot = f"{chr(65+q)}{s}"
            if t == "---":
                T[(q, s)] = None
            else:
                T[(q, s)] = (int(t[0]), 1 if t[1] == "R" else -1, ord(t[2]) - 65, slot)
    return T

def trace_transitions(m, tape_dict, head_pos, init_q, stop_fn, max_steps=2000000):
    """Simulate TM and record set of used slots X and guard pairs (X, next_sym)."""
    T = parse_tm(m)
    tape = dict(tape_dict)
    p = head_pos
    q = init_q
    lo = min(tape.keys()) if tape else 0
    hi = max(tape.keys()) if tape else 0
    lo = min(lo, p)
    hi = max(hi, p)
    slots = set()
    pairs = set()
    first_step = {}
    for st in range(1, max_steps + 1):
        s = tape.get(p, 0)
        tr = T[(q, s)]
        slot = f"{chr(65+q)}{s}"
        slots.add(slot)
        if slot not in first_step:
            first_step[slot] = st
        if tr is None:
            return "HALT", st, slots, pairs, tape, p, q
        w, d, nq, _ = tr
        tape[p] = w
        p += d
        q = nq
        ns = tape.get(p, 0)
        pairs.add(f"{slot}:{ns}")
        if f"{slot}:{ns}" not in first_step:
            first_step[f"{slot}:{ns}"] = st
        side = None
        if p < lo:
            lo = p
            side = "L"
        elif p > hi:
            hi = p
            side = "R"
        if stop_fn(st, q, side, p, lo, hi, tape):
            return "STOP", st, slots, pairs, tape, p, q
    return "LIMIT", max_steps, slots, pairs, tape, p, q

# 1. Profile F5 (all 3 siblings)
F5_SIBS = [
    ("F5-M1", "1RB1RG_0LC0LD_1RF0LD_0RE1LB_1LB0RF_0RA---_1RA1RD", 3, "L"),
    ("F5-M2", "1RB1RE_1RC1RA_0LD0LE_1RF0LE_0RG1LC_0RB---_1LC0RF", 4, "L"),
    ("F5-M3", "1RB0LD_0RC0RG_1LD0RG_0LE---_1LB1LF_1LE1LG_0LA1RB", 6, "R"),
]

def f5_tape(st_tuple, q_idx, side):
    A, L, c = st_tuple
    s = "10"*A + "0" + "".join("10"*d + "0" for d in L[:-1]) + "10"*L[-1] + "1"
    if c >= 0:
        s += "10"*c + "1"
    if side == "L":
        bits = "000" + s
        tape = {i: int(ch) for i, ch in enumerate(bits)}
        return tape, 0, q_idx
    else:
        bits = s[::-1] + "000"
        tape = {i: int(ch) for i, ch in enumerate(bits)}
        return tape, len(bits) - 1, q_idx

print("=================================================================")
print("1. F5 FAMILY TRANSITION & GUARD-PAIR PROFILE")
print("=================================================================")
for name, m, fq, fside in F5_SIBS:
    # Blank startup to step 7205 ([2 | 2^25, 0#])
    _, _, s_start, p_start, _, _, _ = trace_transitions(
        m, {}, 0, 0, lambda st, q, side, p, lo, hi, tp: st >= 7500
    )
    # Engine: D and B_j (ordinary source and attached e>=2 source)
    s_eng, p_eng = set(), set()
    eng_configs = [
        ("D_ord", (4, (2, 2, 0), -1)),
        ("D_att", (4, (3,), -1)),
        ("D_att_c", (4, (3,), 5)),
        ("B1_ord", (6, (0, 4, 2, 0), -1)),
        ("B2_ord", (8, (0, 0, 4, 0), -1)),
        ("B3_ord", (10, (0, 0, 0, 6, 0), -1)),
        ("B1_att", (6, (0, 4), -1)),
        ("B2_att", (8, (0, 0, 4), -1)),
        ("B1_att_c", (6, (0, 3), 5)),
        ("B2_att_c", (8, (0, 0, 3), 5)),
    ]
    per_rule_slots = {}
    per_rule_pairs = {}
    for rname, cfg in eng_configs:
        tp, hp, iq = f5_tape(cfg, fq, fside)
        res, st, sl, pr, _, _, _ = trace_transitions(
            m, tp, hp, iq, lambda st, q, side, p, lo, hi, tp: (q == fq and side == fside)
        )
        s_eng |= sl
        p_eng |= pr
        per_rule_slots[rname] = sl
        per_rule_pairs[rname] = pr

    # Exhaustion / Rebuild: T_k (k=1,2,3), M_j (j=1,2,3), T_0 (c=-1 and c>=1)
    exh_configs = [
        ("T1_no_c", (6, (0, 0), -1)),
        ("T2_no_c", (8, (0, 0, 0), -1)),
        ("T3_no_c", (10, (0, 0, 0, 0), -1)),
        ("T1_with_c", (6, (0, 0), 5)),
        ("M1_with_c", (6, (0, 1), 5)),
        ("M2_with_c", (8, (0, 0, 1), 5)),
        ("M3_with_c", (10, (0, 0, 0, 1), 5)),
        ("M1_no_c", (6, (0, 1), -1)),
        ("T0_with_c", (6, (0,), 5)),
        ("T0_no_c", (6, (0,), -1)),
    ]
    s_exh, p_exh = set(), set()
    for rname, cfg in exh_configs:
        tp, hp, iq = f5_tape(cfg, fq, fside)
        res, st, sl, pr, _, _, _ = trace_transitions(
            m, tp, hp, iq, lambda st, q, side, p, lo, hi, tp: (q == fq and side == fside)
        )
        s_exh |= sl
        p_exh |= pr
        per_rule_slots[rname] = sl
        per_rule_pairs[rname] = pr

    # Also separate D + B_j (pure ordinary interior engine, before touching #) vs touching #
    s_pure_ord = per_rule_slots["D_ord"] | per_rule_slots["B1_ord"] | per_rule_slots["B2_ord"] | per_rule_slots["B3_ord"]
    p_pure_ord = per_rule_pairs["D_ord"] | per_rule_pairs["B1_ord"] | per_rule_pairs["B2_ord"] | per_rule_pairs["B3_ord"]

    print(f"\n[{name}] {m}")
    print(f"  Startup slots ({len(s_start)}): {sorted(s_start)}")
    print(f"  Pure ordinary (D, Bj_ord) slots ({len(s_pure_ord)}): {sorted(s_pure_ord)}")
    print(f"  Full Engine (D, Bj_ord, Bj_att) slots ({len(s_eng)}): {sorted(s_eng)}")
    print(f"  Exhaustion (Tk, Mj, T0) slots ({len(s_exh)}): {sorted(s_exh)}")
    print(f"  Slots in Exhaustion/Attached but NOT Pure Ordinary: {sorted((s_eng | s_exh) - s_pure_ord)}")
    print(f"  Slots in Exhaustion (Tk, Mj, T0) but NOT Engine (D, Bj): {sorted(s_exh - s_eng)}")
    print(f"  Pairs in Exhaustion/Attached but NOT Pure Ordinary: {sorted((p_eng | p_exh) - p_pure_ord)}")
    print(f"  Pairs in Exhaustion (Tk, Mj, T0) but NOT Engine (D, Bj): {sorted(p_exh - p_eng)}")
    for rname in ["T1_no_c", "T2_no_c", "M1_with_c", "M2_with_c", "T0_with_c", "T0_no_c"]:
        diff_p = sorted(per_rule_pairs[rname] - p_pure_ord)
        diff_e = sorted(per_rule_pairs[rname] - p_eng)
        print(f"    {rname:12s}: vs_ord={diff_p} | vs_all_eng={diff_e}")

# 2. Profile F89
print("\n=================================================================")
print("2. F89 FAMILY TRANSITION & GUARD-PAIR PROFILE")
print("=================================================================")
F89 = "1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE"

def f89_tape(digs):
    # [D on new left cell] 0 0 [1 (01)^d1] [1 (01)^d2] ...
    bits = "000" + "".join("1" + "01"*d for d in digs)
    tape = {i: int(ch) for i, ch in enumerate(bits)}
    return tape, 0, 3 # D=3

def f89_is_p1(q, side, p, tape):
    if q != 3 or side != "L":
        return False
    # check if tape at p+1, p+2, p+3 is 0, 0, 1
    return tape.get(p+1, 0) == 0 and tape.get(p+2, 0) == 0 and tape.get(p+3, 0) == 1

_, _, f89_s_start, f89_p_start, _, _, _ = trace_transitions(
    F89, {}, 0, 0, lambda st, q, side, p, lo, hi, tp: st >= 4679
)

f89_rules = [
    ("D", [3, 5, 3]),
    ("D_end", [3, 5]),
    ("B1", [3, 1, 5, 3]),
    ("B2", [3, 1, 1, 5, 3]),
    ("B3", [3, 1, 1, 1, 5]),
    ("B6", [5, 1, 1, 1, 1, 1, 1, 5]),
    ("T1", [3, 1]),
    ("T2", [3, 1, 1]),
    ("T3", [3, 1, 1, 1]),
    ("T6", [5, 1, 1, 1, 1, 1, 1]),
    ("S_3", [3]),
    ("S_5", [5]),
    ("S_7", [7]),
]
f89_r_slots = {}
f89_r_pairs = {}
for rname, digs in f89_rules:
    tp, hp, iq = f89_tape(digs)
    res, st, sl, pr, _, _, _ = trace_transitions(
        F89, tp, hp, iq, lambda st, q, side, p, lo, hi, tp: f89_is_p1(q, side, p, tp)
    )
    f89_r_slots[rname] = sl
    f89_r_pairs[rname] = pr

s_f89_eng = f89_r_slots["D"] | f89_r_slots["D_end"] | f89_r_slots["B1"] | f89_r_slots["B2"] | f89_r_slots["B3"] | f89_r_slots["B6"]
p_f89_eng = f89_r_pairs["D"] | f89_r_pairs["D_end"] | f89_r_pairs["B1"] | f89_r_pairs["B2"] | f89_r_pairs["B3"] | f89_r_pairs["B6"]
s_f89_tk = f89_r_slots["T1"] | f89_r_slots["T2"] | f89_r_slots["T3"] | f89_r_slots["T6"]
p_f89_tk = f89_r_pairs["T1"] | f89_r_pairs["T2"] | f89_r_pairs["T3"] | f89_r_pairs["T6"]
s_f89_S = f89_r_slots["S_3"] | f89_r_slots["S_5"] | f89_r_slots["S_7"]
p_f89_S = f89_r_pairs["S_3"] | f89_r_pairs["S_5"] | f89_r_pairs["S_7"]

print(f"F89 Startup slots ({len(f89_s_start)}): {sorted(f89_s_start)}")
print(f"F89 Engine (D, Bk) slots ({len(s_f89_eng)}): {sorted(s_f89_eng)}")
print(f"F89 Engine (D, Bk) pairs ({len(p_f89_eng)}): {sorted(p_f89_eng)}")
print(f"F89 Top-shrink (Tk) slots ({len(s_f89_tk)}): {sorted(s_f89_tk)}")
print(f"F89 Rebuild (S) slots ({len(s_f89_S)}): {sorted(s_f89_S)}")
print(f"F89 Slots in Tk|S but NOT Engine: {sorted((s_f89_tk | s_f89_S) - s_f89_eng)}")
print(f"F89 Pairs in Tk but NOT Engine: {sorted(p_f89_tk - p_f89_eng)}")
print(f"F89 Pairs in S but NOT Engine: {sorted(p_f89_S - p_f89_eng)}")
print(f"F89 Pairs in S but NOT (Engine | Tk): {sorted(p_f89_S - (p_f89_eng | p_f89_tk))}")
for rname, _ in f89_rules:
    print(f"  {rname:8s}: slots={sorted(f89_r_slots[rname])} | extra_pairs_vs_DB={sorted(f89_r_pairs[rname] - p_f89_eng)}")

# 3. Check X33, Z16, Y19, F70, F279, F141 in m8sweep xcands
print("\n=================================================================")
print("3. X33, Z16, Y19, F70, F279, F141 IN m8sweep/xcands.json")
print("=================================================================")
extra_hosts = {
    "X33": "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE",
    "Z16": "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LA1LG_---0LE",
    "Y19": "1RB1RA_0RC0RA_0LD1RC_0LE1LE_---1LF_1LA0LG_1LB1LG",
    "F70": "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LG0LE_1RA---",
    "F279": "1RB0LA_0RC0RG_1RD---_0LE0LF_1LE0RF_1LF1RA_0RD0RG",
    "F44a": "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LG0LE_0RA---",
    "F44b": "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LG0LE_1RE---",
    "F86": "1RB---_1RC1RB_0RD0RB_0LE1RD_0LF1LG_1LC1LF_1LA0LF",
    "F141a": "1RB0RC_1LC0LG_1RA1RD_0RE0LD_1LB1RF_0RA---_1LB1LB",
    "F141b": "1RB1RD_1RC0RA_1LA0LG_0RE0LD_1LC1RF_0RB---_1RG1LC",
    "F141c": "1RB1LF_1RC0RG_1LD1LE_1LB0LC_0LA0RE_0LD---_1RB1RB",
}
for k, m in extra_hosts.items():
    r = xc_map.get(m)
    if r:
        sf = os.path.join(M8_DIR, "scr", f"{r['i']:03d}.json")
        print(f"  {k:6s} (i={r['i']:3d}): free={r['free']} guards={r['guards']} scr_done={os.path.exists(sf)}")
    else:
        print(f"  {k:6s}: NOT in m8sweep xcands.json")
