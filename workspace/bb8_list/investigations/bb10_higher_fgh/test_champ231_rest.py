import sys
from test_champ231_10state import parse_tm, fmt_tm, run_sim, solve_traj

# Part 1: Fast scan of P5, CASCADE, CAP_1RI_1RA0LF
REST_PARENTS = [
    ("P5_---0LI_1LG0LH (P5)",   "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1LG0LH", 21, [16, 17, 18, 19, 20, 21, 26]),
    ("CASCADE_---1LI_1RB1LH",   "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1LI_1RB1LH", 20, [16, 17, 18, 19, 20, 21]),
    ("CAP_1RI_1RA0LF",          "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_1RA0LF", 21, [15, 18, 20, 21, 24, 27]),
]

for label, tm9, k_halt, probe_ks in REST_PARENTS:
    tr9 = parse_tm(tm9)
    is_232 = "_1LC0RB_" in tm9
    snaps = {k: run_sim(tr9, k, 2*k + 10, is_232=is_232, save_snap=True) for k in probe_ks}
    kd0, slot_name, h_slot, c0, snap0 = snaps[k_halt]
    print(f"\n=======================================================")
    print(f"PARENT: {label} | {tm9} | k_halt={k_halt} -> {kd0} at {slot_name} (c={c0})")
    tape0, lo0, hi0, h0, q0, step0, col0, aj0 = snap0
    k_reb = 0
    h_del = []
    mixed = []
    all_k_ex = []
    for hw in ['0', '1']:
        for hd, step_d in [('L', -1), ('R', 1)]:
            h_act = f"{hw}{hd}J"
            c1 = tape0[h0 + step_d]
            j_slot1 = 2 * 9 + c1
            for jw in ['0', '1']:
                for jd in ['L', 'R']:
                    for jnx_idx in range(10):
                        j_act = f"{jw}{jd}{chr(65 + jnx_idx)}"
                        tr10 = list(tr9) + ["---", "---"]
                        tr10[h_slot] = h_act
                        tr10[j_slot1] = j_act
                        kd, dL, I, c, _ = run_sim(tr10, k_halt, 2*k_halt + 10, is_232=is_232, snap_in=snap0)
                        if kd in ("K", "K*"):
                            k_reb += 1
                            # Check probe_ks
                            outcomes = {}
                            for pk in probe_ks:
                                p_res = snaps[pk]
                                if p_res[0] in ("K", "K*"):
                                    outcomes[pk] = p_res[:4]
                                else:
                                    r_pk = run_sim(tr10, pk, 2*pk + 10, is_232=is_232, snap_in=p_res[4])
                                    outcomes[pk] = r_pk[:4]
                            has_h = [pk for pk, v in outcomes.items() if v[0] in ("H", "H*")]
                            has_t = [pk for pk, v in outcomes.items() if v[0] == "T"]
                            if has_h:
                                mixed.append((h_act, j_slot1, j_act, tr10, outcomes))
                            elif not has_t and len(all_k_ex) < 8:
                                all_k_ex.append((h_act, j_slot1, j_act, kd, dL, I, c))
                        elif kd in ("H", "H*") and c > c0:
                            h_del.append((h_act, j_slot1, j_act, kd, dL, c))
    print(f"  160 lazy-TNF J-extensions on k={k_halt}: K-rebuilders={k_reb}, Mixed(K+H on probe)={len(mixed)}, delayed-H={len(h_del)}")
    for h_act, j_slot1, j_act, kd, slot_h, c in sorted(h_del, key=lambda x: -x[5])[:8]:
        print(f"    [Delayed H] {slot_name}={h_act} J{j_slot1-18}={j_act} -> {kd} at {slot_h} with c={c} (was {c0})")
    for h_act, j_slot1, j_act, tr10, outcomes in mixed:
        print(f"    [Mixed K+H] {slot_name}={h_act} J{j_slot1-18}={j_act} -> {outcomes}")
    for h_act, j_slot1, j_act, kd, dL, I, c in all_k_ex:
        print(f"    [All-K sample] {slot_name}={h_act} J{j_slot1-18}={j_act} -> k={k_halt}: {kd} dL={dL} I={I} c={c}")

# Part 2: Check ALL c=0 E3 halters on k=19 (3 mod 4) AND k=21 (1 mod 4)
E3_FAM = [
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RD0RI_0LG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LE0RI_0LG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RI0RI_0LG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RD0RI_1LH---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB1RI_0LD---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RD1RI_0LD---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LE1RI_0LD---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB1RI_1RG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RD1RI_1RG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LE1RI_1RG---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_1RD0RI_1LH---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_0RB1RI_0LD---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_1RD1RI_0LD---",
    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_1LE1RI_0LD---",
]

print("\n=======================================================")
print("PART 2: Checking all 15 E3 (P=2) halters for k=19 vs k=21 residue splitting")
for tm9 in E3_FAM:
    tr9 = parse_tm(tm9)
    is_232 = "_1LC0RB_" in tm9
    s19 = run_sim(tr9, 19, 48, is_232=is_232, save_snap=True)
    s21 = run_sim(tr9, 21, 52, is_232=is_232, save_snap=True)
    h_slot = s19[2]
    tape19, h19 = s19[4][0], s19[4][3]
    splits = []
    for hw in ['0', '1']:
        for hd, step_d in [('L', -1), ('R', 1)]:
            h_act = f"{hw}{hd}J"
            c1 = tape19[h19 + step_d]
            j_slot1 = 2 * 9 + c1
            for jw in ['0', '1']:
                for jd in ['L', 'R']:
                    for jnx_idx in range(10):
                        j_act = f"{jw}{jd}{chr(65 + jnx_idx)}"
                        tr10 = list(tr9) + ["---", "---"]
                        tr10[h_slot] = h_act
                        tr10[j_slot1] = j_act
                        r19 = run_sim(tr10, 19, 48, is_232=is_232, snap_in=s19[4])
                        r21 = run_sim(tr10, 21, 52, is_232=is_232, snap_in=s21[4])
                        k19_is_K = r19[0] in ("K", "K*")
                        k21_is_K = r21[0] in ("K", "K*")
                        k19_is_H = r19[0] in ("H", "H*")
                        k21_is_H = r21[0] in ("H", "H*")
                        if (k19_is_K and k21_is_H) or (k21_is_K and k19_is_H):
                            splits.append((h_act, j_slot1, j_act, tr10, r19[:4], r21[:4]))
    if splits:
        print(f"  {tm9}: {len(splits)} mod-4 splitters found!", flush=True)
        # Precompute parent on k=12..35 once!
        p_even = {k: run_sim(tr9, k, 2*k+10, is_232=is_232) for k in range(12, 36, 2)}
        p_odd_n1 = {k: run_sim(tr9, k, 2*k+10, is_232=is_232, save_snap=True) for k in range(13, 36, 2)}
        p_odd_n2 = {k: run_sim(tr9, k, 2*k+20, is_232=is_232, save_snap=True) for k in range(13, 36, 2)}
        p_odd_c12 = {k: run_sim(tr9, k, 2*k+10, is_232=is_232, capx=12, save_snap=True) for k in range(13, 36, 2)}
        for h_act, j_slot1, j_act, tr10, r19, r21 in splits:
            ks_res = {}
            rob_ok = True
            for k in range(12, 36):
                if k % 2 == 0:
                    rn1 = p_even[k]
                    ks_res[k] = ("K", rn1[1], rn1[2])
                else:
                    rn1 = run_sim(tr10, k, 2*k+10, is_232=is_232, snap_in=p_odd_n1[k][4])
                    rn2 = run_sim(tr10, k, 2*k+20, is_232=is_232, snap_in=p_odd_n2[k][4])
                    rc12 = run_sim(tr10, k, 2*k+10, is_232=is_232, capx=12, snap_in=p_odd_c12[k][4])
                    if rn1[0] in ("H", "H*") and rn2[0] in ("H", "H*"):
                        ks_res[k] = ("H", 0, 0)
                    elif rn1[0] in ("K", "K*") and rn2[0] in ("K", "K*") and rn1[1] == rn2[1] and rn1[2] == rn2[2]:
                        if rc12[1] != rn1[1] or rc12[2] != rn1[2]: rob_ok = False
                        ks_res[k] = ("K", rn1[1], rn1[2])
                    else:
                        ks_res[k] = ("X", 0, 0)
            res_s, r_s, traj_s = solve_traj(ks_res, kmax=35)
            print(f"    I1={h_act} J{j_slot1-18}={j_act} | k19={r19[:3]} k21={r21[:3]} | solve={res_s} R={r_s} rob={rob_ok} traj={traj_s}", flush=True)
