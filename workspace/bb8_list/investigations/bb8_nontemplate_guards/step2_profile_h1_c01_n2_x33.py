import os
from step1_profile_transitions import parse_tm, trace_transitions

# Let's profile:
# 1. H1, H2, c01, c02, H4 (from nonlist / h1_extend)
# 2. N2, N2m (from n2_decide)
# 3. X33, Z16, Y19 (from x33check)
# 4. Exact prelude steps of F89 and F89-S1..S3

F89_ALL = [
    ("F89",    "1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE", 4679),
    ("F89-S1", "1RB0LG_1LC0LE_1LF0LD_1RE0RB_1RB0RD_0LA---_1LA1LD", 162),
    ("F89-S2", "1RB0RD_1LC0LA_1LE0LD_1RA0RB_0LF---_1RB0LG_1LF1LD", 162),
    ("F89-S3", "1RB0RF_1RC0RE_0RD---_1LA0RG_1LF0LA_1LA0LE_1RD1RE", 13),
]

print("=================================================================")
print("1. F89 & SIBLINGS EXACT PRELUDE STEP-BY-STEP FOR RARE PAIRS")
print("=================================================================")
for name, m, pre_step in F89_ALL:
    T = parse_tm(m)
    tape = {}
    p = 0
    q = 0
    slot_steps = {}
    pair_steps = {}
    for st in range(1, pre_step + 2000):
        s = tape.get(p, 0)
        slot = f"{chr(65+q)}{s}"
        tr = T[(q, s)]
        w, d, nq, _ = tr
        tape[p] = w
        p += d
        q = nq
        ns = tape.get(p, 0)
        pair = f"{slot}:{ns}"
        slot_steps.setdefault(slot, []).append(st)
        pair_steps.setdefault(pair, []).append(st)
    print(f"\n[{name}] (pre_step={pre_step})")
    for pr, sts in sorted(pair_steps.items()):
        if len(sts) <= 40:
            print(f"  Pair {pr:5s} (count={len(sts):2d}): steps={sts}")

# 2. Profile H1, H2, c01, c02
print("\n=================================================================")
print("2. H1, H2, c01, c02 TRANSITION & GUARD-PAIR PROFILE")
print("=================================================================")
H1 = "1RB1RE_1RC1RA_0LD1LE_1RE1LE_0RG0RF_---0LG_1LC1RA"
H2 = "1RB1RF_0LC1LD_1RD1LD_0RE0RG_1LB1RF_1RA1RD_---0LE"
c01 = "1RB---_0RC0RA_0RD1LG_0LE1RC_1RF0LF_1LE1LD_0LD0LB"
c02 = "1RB---_0RC0RA_0RD1LG_0LE1RC_1RF0LF_1LE1LD_0RD0LB"

def build_k2_tape(tmpl_str):
    """Parse xs.cpp template like 'E 1 | [10] 10^1 01^5 00 10' into (tape_dict, head_pos, init_q)."""
    toks = tmpl_str.split()
    q = ord(toks[0]) - 65
    side = int(toks[1])
    bits_L = ""
    bits_cur = ""
    bits_R = ""
    right = False
    for t in toks[2:]:
        if t == "|":
            continue
        if t.startswith("["):
            bits_cur = t[1:-1]
            right = True
            continue
        if "^" in t:
            b, n = t.split("^")
            s = b * int(n)
        else:
            s = t
        if not right:
            bits_L += s
        else:
            bits_R += s
    full = bits_L + bits_cur + bits_R
    head_pos = len(bits_L) + (len(bits_cur) - 1 if side == 1 else 0)
    tape = {i: int(ch) for i, ch in enumerate(full)}
    return tape, head_pos, q

# For H1:
# Startup: blank tape 1..10000 steps (builds the 20-group list at ~6847 steps)
_, _, h1_s_start, h1_p_start, _, _, _ = trace_transitions(
    H1, {}, 0, 0, lambda st, q, side, p, lo, hi, tp: st >= 10000
)
# Engine templates (L1, L2, Lx, Ly, Borrow over k empty groups):
h1_eng_tmpls = [
    ("L1_step", "E 1 | [10] 10^3 01^8 00 10^2 01^3 00 10 01"),
    ("L2_step", "E 1 | [10] 01^8 00 01^3 00 10 01"),
    ("Lx_step", "E 1 | [10] 01^8 00 00 10^2 01^2 00 10 01"),
    ("Ly_step", "E 1 | [10] 01^8 00 00 01^2 00 10 01"),
    ("Borrow_1", "E 1 | [10] 01^8 00 00 10 01 00 10 01"),
    ("Borrow_2", "E 1 | [10] 01^8 00 00 00 10 01 00 10 01"),
    ("Borrow_3", "E 1 | [10] 01^8 00 00 00 00 10 01 00 10 01"),
]
h1_s_eng, h1_p_eng = set(), set()
for rname, tmpl in h1_eng_tmpls:
    tp, hp, iq = build_k2_tape(tmpl)
    _, _, sl, pr, _, _, _ = trace_transitions(
        H1, tp, hp, iq, lambda st, q, side, p, lo, hi, tp: st >= 30000
    )
    h1_s_eng |= sl
    h1_p_eng |= pr

# Exhaustion templates for H1 (from h1_extend/REPORT.txt & nonlist/hand/tier1_real.txt):
# E|10^2 01^b 00 10, E|11 01^b 00 10, C|10 01^b 00 10, D 1 | [11] 01^N for b/N in 3..18 (covering all mod 8 classes)
h1_s_exh, h1_p_exh = set(), set()
for b in range(3, 19):
    for tmpl in [
        f"E 1 | [10] 10^1 01^{b} 00 10",
        f"E 1 | [11] 01^{b} 00 10",
        f"C 1 | [10] 01^{b} 00 10",
        f"D 1 | [11] 01^{b}",
    ]:
        tp, hp, iq = build_k2_tape(tmpl)
        _, _, sl, pr, _, _, _ = trace_transitions(
            H1, tp, hp, iq, lambda st, q, side, p, lo, hi, tp: st >= 40000
        )
        h1_s_exh |= sl
        h1_p_exh |= pr

print(f"\n[H1] {H1}")
print(f"  Startup slots ({len(h1_s_start)}): {sorted(h1_s_start)}")
print(f"  Engine slots ({len(h1_s_eng)}): {sorted(h1_s_eng)}")
print(f"  Exhaustion slots ({len(h1_s_exh)}): {sorted(h1_s_exh)}")
print(f"  Engine pairs ({len(h1_p_eng)}): {sorted(h1_p_eng)}")
print(f"  Exhaustion pairs ({len(h1_p_exh)}): {sorted(h1_p_exh)}")
print(f"  Slots in Exhaustion but NOT Engine: {sorted(h1_s_exh - h1_s_eng)}")
print(f"  Pairs in Exhaustion but NOT Engine: {sorted(h1_p_exh - h1_p_eng)}")

# Let's also check H1 natural run step-by-step for when each slot and pair is used!
T_h1 = parse_tm(H1)
tp_h1 = {}; p_h1 = 0; q_h1 = 0
h1_pair_steps = {}
for st in range(1, 200000):
    s = tp_h1.get(p_h1, 0)
    slot = f"{chr(65+q_h1)}{s}"
    w, d, nq, _ = T_h1[(q_h1, s)]
    tp_h1[p_h1] = w; p_h1 += d; q_h1 = nq
    ns = tp_h1.get(p_h1, 0)
    h1_pair_steps.setdefault(f"{slot}:{ns}", []).append(st)
print("  H1 natural run (200,000 steps) pair counts (build finishes around step ~6847):")
for pr, sts in sorted(h1_pair_steps.items()):
    after = [x for x in sts if x > 8000]
    print(f"    {pr:5s}: total={len(sts):6d}, <=8000={len([x for x in sts if x<=8000]):4d}, >8000={len(after):6d} (last={sts[-1]})")

# Same for c01 and c02!
for cname, cm in [("c01", c01), ("c02", c02)]:
    T_c = parse_tm(cm)
    tp_c = {}; p_c = 0; q_c = 0
    c_pair_steps = {}
    # In c01, natural start builds 1533-item list around step 1.27e7! Let's check constructed engine vs exhaustion templates first
    c_eng_tmpls = [
        ("L1", "C 0 | 01 10 00 01 10 00 10^4 01^6 [00]"),
        ("Lx", "C 0 | 01 10 00 01 10 00 00 10^6 01^4 [00]"),
        ("Ly", "C 0 | 01 10 00 01 00 00 01^6 [00]"),
        ("Bor1", "C 0 | 01 10 00 01 10 00 00 00 01^8 [00]"),
        ("Bor2", "C 0 | 01 10 00 01 10 00 00 00 00 01^8 [00]"),
    ]
    c_s_eng, c_p_eng = set(), set()
    for rname, tmpl in c_eng_tmpls:
        tp, hp, iq = build_k2_tape(tmpl)
        _, _, sl, pr, _, _, _ = trace_transitions(
            cm, tp, hp, iq, lambda st, q, side, p, lo, hi, tp: st >= 30000
        )
        c_s_eng |= sl
        c_p_eng |= pr
    c_s_exh, c_p_exh = set(), set()
    for qv in range(4, 16):
        for pv in range(1, 5):
            tmpl = f"C 0 | 01 00 10^{qv} 01^{pv} [00]"
            tp, hp, iq = build_k2_tape(tmpl)
            _, _, sl, pr, _, _, _ = trace_transitions(
                cm, tp, hp, iq, lambda st, q, side, p, lo, hi, tp: st >= 30000
            )
            c_s_exh |= sl
            c_p_exh |= pr
    print(f"\n[{cname}] {cm}")
    print(f"  Engine slots ({len(c_s_eng)}): {sorted(c_s_eng)}")
    print(f"  Exhaustion slots ({len(c_s_exh)}): {sorted(c_s_exh)}")
    print(f"  Slots in Exhaustion but NOT Engine: {sorted(c_s_exh - c_s_eng)}")
    print(f"  Pairs in Exhaustion but NOT Engine: {sorted(c_p_exh - c_p_eng)}")
    print(f"  Engine pairs ({len(c_p_eng)}): {sorted(c_p_eng)}")
    print(f"  Exhaustion pairs ({len(c_p_exh)}): {sorted(c_p_exh)}")
