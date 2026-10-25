import os, sys
from step4_analyze_f5_redirects import F5_M1, F5_M2, F5_M3, parse_tm, build_m3_tape, parse_m3_k, run_m3_macro

print("=================================================================")
print("1. F5-M1, M2, M3 PRELUDE VS POST-PRELUDE (X, s) PAIRS")
print("=================================================================")

for name, code, pre_step in [("F5-M1", F5_M1, 165), ("F5-M2", F5_M2, 33), ("F5-M3", F5_M3, 162)]:
    trans = parse_tm(code)
    tape = {}
    head = 0
    st = 'A'
    pre_pairs = set()
    post_pairs = set()
    for step in range(1, 30000):
        cur = tape.get(head, 0)
        slot = f"{st}{cur}"
        w, d, nxt = trans[(st, cur)]
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d
        st = nxt
        nxt_sym = tape.get(head, 0)
        pair = f"{slot}:{nxt_sym}"
        if step <= pre_step:
            pre_pairs.add(pair)
        else:
            post_pairs.add(pair)
    print(f"[{name}] pre_step={pre_step}:")
    print(f"  pre_pairs ({len(pre_pairs)}): {sorted(pre_pairs)}")
    print(f"  post_pairs ({len(post_pairs)}): {sorted(post_pairs)}")
    print(f"  Pairs in Prelude ONLY (never used after step {pre_step}): {sorted(pre_pairs - post_pairs)}")

print("\n=================================================================")
print("2. CHECK F5-M3 GUARD REDIRECTS FOR ANY OUT-OF-INVARIANT K-CONFIGS")
print("=================================================================")
# For all 21*33 = 693 active guard redirects (and D0:0) on F5-M3:
# Run from blank tape for 10,000 steps, collect all K-configs (A, L, c) reached,
# and check if ANY guard redirect reaches a K-config of length |L| >= 3 that violates the F5 invariant
# (i.e. A odd, or any d_i odd for i < len(L)-1, or L[-1] + (c+1) odd, or below threshold)!
STATES_8 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
ALL_ACTIONS = [None]
for w in (0, 1):
    for d in (-1, 1):
        for s in STATES_8:
            ALL_ACTIONS.append((w, d, s))

t_m3 = parse_tm(F5_M3)

def run_m3_blank_k(trans, max_steps=10000):
    tape = {}
    head = 0
    st = 'A'
    max_vis = 0
    ks = []
    for step in range(1, max_steps + 1):
        cur = tape.get(head, 0)
        tr = trans.get((st, cur))
        if tr is None:
            return ("HALT", step, f"{st}{cur}", ks)
        w, d, nxt = tr
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d
        st = nxt
        if head > max_vis:
            max_vis = head
            cfg = parse_m3_k(tape, head, st, max_vis)
            if cfg is not None:
                ks.append((step, cfg))
    return ("TIMEOUT", max_steps, None, ks)

def is_in_f5_inv(cfg):
    A, L, c = cfg
    if A < 2 or A % 2 != 0:
        return False
    for d in L[:-1]:
        if d % 2 != 0:
            return False
    e = L[-1]
    if c == -1:
        if e % 2 != 0:
            return False
    else:
        if e != 1 or c % 2 != 1:
            return False
    return True

out_of_inv_towers = []
for s_idx in range(7):
    st_x = chr(ord('A') + s_idx)
    for sym_x in (0, 1):
        slot = f"{st_x}{sym_x}"
        if slot == "D1": continue
        old_w, old_d, old_nxt = t_m3[(st_x, sym_x)]
        for s_guard in (0, 1):
            other_sym = 1 - s_guard
            old_other = t_m3.get((old_nxt, other_sym))
            for act in ALL_ACTIONS:
                if act == t_m3.get((old_nxt, s_guard)):
                    continue
                t = dict(t_m3)
                t[(st_x, sym_x)] = (old_w, old_d, 'H')
                t[('H', other_sym)] = old_other
                t[('H', s_guard)] = act
                r = run_m3_blank_k(t, max_steps=9000)
                if r[0] == "TIMEOUT" and len(r[3]) > 0:
                    # Check if any K-config with len(L) >= 3 is out of invariant or if the machine is still in a tower
                    big_ks = [(stp, cfg) for stp, cfg in r[3] if len(cfg[1]) >= 3]
                    if big_ks:
                        # Check if it's identical to base F5-M3 trajectory (which has 44 K-events up to 9000)
                        last_stp, last_cfg = r[3][-1]
                        if not is_in_f5_inv(last_cfg) or last_cfg != (22, [19, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0], -1):
                            out_of_inv_towers.append((f"{slot}:{s_guard}", act, len(r[3]), big_ks[0], r[3][-1]))

print(f"F5-M3 guard redirects with TIMEOUT@9000 and non-identical tower K-configs (len>=3): {len(out_of_inv_towers)}")
for gp, act, kcnt, bk0, kl in out_of_inv_towers[:30]:
    print(f"  guard={gp} act={act} kcnt={kcnt} first_big={bk0[1]}@{bk0[0]} last={kl[1]}@{kl[0]} in_inv={is_in_f5_inv(kl[1])}")
