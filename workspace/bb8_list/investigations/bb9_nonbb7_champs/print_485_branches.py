import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from backtrack_c4_9state import parse_tm, make_exhaustion_tape, check_valid_odd_k, run_fixed_tm

base_tr = parse_tm("1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB")
all_moves_9 = [(w, d, ns) for w in (0, 1) for d in (-1, 1) for ns in range(9)]
c1_moves = [(w, d, 7) for w in (0, 1) for d in (-1, 1)]

survivors = []
def backtrack(tr, assigned_slots, tape, head, state, step):
    while step <= 850:
        v = tape.get(head, 0)
        if state == 4 and v == 0:
            vok = check_valid_odd_k(tape, head, state)
            if vok is not None:
                survivors.append((dict(tr), list(assigned_slots), step, vok[0], vok[1]))
                return
        key = (state, v)
        if key in tr:
            w, d, ns = tr[key]
            if w == 0: tape.pop(head, None)
            else: tape[head] = 1
            head += d; state = ns
            step += 1
        else:
            if len(assigned_slots) >= 4:
                return
            cand_moves = c1_moves if key == (2, 1) else all_moves_9
            for mv in cand_moves:
                tr[key] = mv
                assigned_slots.append(key)
                t_copy = dict(tape)
                w, d, ns = mv
                if w == 0: t_copy.pop(head, None)
                else: t_copy[head] = 1
                backtrack(tr, assigned_slots, t_copy, head + d, ns, step + 1)
                assigned_slots.pop()
                del tr[key]
            return

tape0, head0, state0 = make_exhaustion_tape(k=3, M=4)
backtrack(dict(base_tr), [], tape0, head0, state0, 1)

classes = {}
for tr, slots, s3, b3, ds3 in survivors:
    r3_m5 = run_fixed_tm(tr, k=3, M=5, max_steps=1200)
    if r3_m5[0] != "VALID_ODD_K" or r3_m5[3] != ds3 + [1]:
        continue
    r21 = run_fixed_tm(tr, k=21, M=4, max_steps=15000)
    if r21[0] != "VALID_ODD_K":
        continue
    r4 = run_fixed_tm(tr, k=4, M=4, max_steps=5000)
    sig = (b3, tuple(ds3), r21[2], tuple(r21[3][:4]), len(r21[3]), r4[0], r4[2] if r4[0]=="VALID_ODD_K" else None)
    classes.setdefault(sig, []).append((tr, slots, s3, r21[1], r4))

print(f"Found {len(classes)} classes among the good_21 branches:")
for sig, items in classes.items():
    tr, slots, s3, s21, r4 = items[0]
    slot_str = " ".join(f"{chr(ord('A')+k[0])}{k[1]}={tr[k][0]}{'L' if tr[k][1]==-1 else 'R'}{chr(ord('A')+tr[k][2])}" for k in slots)
    print(f"  [{len(items):3d} branches] {slot_str}: k3=(s={s3},B={sig[0]},ds={list(sig[1])}) | k21=(s={s21},B={sig[2]},head={list(sig[3])},len={sig[4]}) | k4={r4[:3]}")
