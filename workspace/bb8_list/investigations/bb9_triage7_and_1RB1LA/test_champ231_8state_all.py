import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
tr_base = [t for row in M1.split("_") for t in (row[:3], row[3:])]

def parse_K_tape(tape, h, s):
    if s != 4 or tape.get(h, 0) != 0:
        return None
    ones = [i for i, v in tape.items() if v == 1]
    if not ones or h >= min(ones):
        return None
    mn, mx = min(ones), max(ones)
    if h != mn - 1:
        return None
    rev_w = "".join(str(tape.get(i, 0)) for i in range(mn, mx + 1))
    w = rev_w[::-1]
    if not (w.startswith("100") and w.endswith("1")) or len(w) < 4:
        return None
    body = w[3:-1]
    parts = body.split("00")
    if len(parts) < 2:
        return None
    vals = []
    for p in parts:
        if len(p) % 2 != 0 or set(p) - {'1'}:
            return None
        vals.append(len(p) // 2)
    return (vals[:-2], vals[-2], vals[-1])

# 1. Check which slots are used in Blank -> step 3715, in D, in Bk, in E (before C1), and after C1!
def get_used_slots(tr, tape, h, s, max_steps):
    used = {}
    for st in range(1, max_steps + 1):
        b = tape.get(h, 0)
        slot = chr(65+s) + str(b)
        used[slot] = used.get(slot, 0) + 1
        act = tr[2*s + b]
        if act == "---":
            return used, ("HALT", st, slot)
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == "R" else -1
        s = ord(act[2]) - 65
        parsed = parse_K_tape(tape, h, s)
        if parsed is not None and st > 10:
            return used, ("K", st, parsed)
    return used, ("T", max_steps, None)

print("=== 1. Slot usage counts in Blank -> K(1^20; 1; 2) (3715 steps) ===")
tape = {}
h, s = 0, 0
used_blank = {}
for st in range(1, 3716):
    b = tape.get(h, 0)
    slot = chr(65+s) + str(b)
    used_blank[slot] = used_blank.get(slot, 0) + 1
    act = tr_base[2*s + b]
    if int(act[0]): tape[h] = 1
    else: tape.pop(h, None)
    h += 1 if act[1] == "R" else -1
    s = ord(act[2]) - 65
print("  Blank (1..3715):", sorted(used_blank.items()))

# Check after step 3715 up to 50,000
used_after = {}
for st in range(3716, 50000):
    b = tape.get(h, 0)
    slot = chr(65+s) + str(b)
    used_after[slot] = used_after.get(slot, 0) + 1
    act = tr_base[2*s + b]
    if int(act[0]): tape[h] = 1
    else: tape.pop(h, None)
    h += 1 if act[1] == "R" else -1
    s = ord(act[2]) - 65
print("  Steps 3716..50000:", sorted(used_after.items()))

# Check E(k=3, a=4) up to C1
rev_w = "100" + "11"*4 + "00" + "00"*3 + "1"
tape_e = {i: int(c) for i, c in enumerate(rev_w) if c == '1'}
used_e, res_e = get_used_slots(tr_base, tape_e, -1, 4, 10000)
print("  E(k=3, a=4) -> C1:", sorted(used_e.items()), res_e)

# 2. Test all 256 8-state {C1, H0, H1} completions (with 1 '---' slot in H) on k = 1..8 (and k = 20)!
print("\n=== 2. Testing all 256 8-state {C1 -> H, H0, H1} completions on C1 config (N=6) ===")
interesting_8 = []
for c1_w in "01":
    for c1_d in "LR":
        c1_act = c1_w + c1_d + "H"
        for halt_bit in (0, 1):
            other_bit = 1 - halt_bit
            for h_w in "01":
                for h_d in "LR":
                    for h_st in "ABCDEFGH":
                        h_act = h_w + h_d + h_st
                        tr = list(tr_base) + ["---", "---"]
                        tr[2*2 + 1] = c1_act
                        tr[2*7 + other_bit] = h_act
                        # Test across k = 1..8 and k = 20
                        outcomes = {}
                        for k in [1, 2, 3, 4, 5, 6, 20]:
                            N = 25 if k == 20 else 6
                            left_str = "10"*(2*k-1) + "11001"
                            right_str = "100" + "1100"*N + "1"
                            full_str = left_str + "1" + right_str
                            h0 = len(left_str)
                            tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
                            h, s = h0, 2
                            out = "T"
                            for step in range(1, 25000):
                                b = tape.get(h, 0)
                                act = tr[2*s + b]
                                if act == "---":
                                    out = f"H@{step}"
                                    break
                                if int(act[0]): tape[h] = 1
                                else: tape.pop(h, None)
                                h += 1 if act[1] == "R" else -1
                                s = ord(act[2]) - 65
                                parsed = parse_K_tape(tape, h, s)
                                if parsed is not None:
                                    ds_o, a_o, b_o = parsed
                                    if b_o == 0 and len(ds_o) >= N - 3:
                                        out = f"K(len={len(ds_o)},a={a_o})"
                                        break
                                # Also check KP with b=0
                                if s == 4 and tape.get(h, 0) == 0 and tape.get(h+1, 0) == 1 and tape.get(h+2, 0) == 0 and tape.get(h+3, 0) == 0:
                                    ones = [i for i, v in tape.items() if v == 1]
                                    left_ones = [i for i in ones if i < h]
                                    if left_ones:
                                        l_str = "".join(str(tape.get(i, 0)) for i in range(min(left_ones), h))
                                        r_str = "".join(str(tape.get(i, 0)) for i in range(h+1, max(ones)+1))
                                        w_r = r_str[::-1]
                                        if w_r.startswith("100") and w_r.endswith("1"):
                                            parts = w_r[3:-1].split("00")
                                            if all(len(p)%2==0 and not (set(p)-{'1'}) for p in parts):
                                                vals = [len(p)//2 for p in parts]
                                                if vals[-1] == 0 and len(vals) - 2 >= N - 3:
                                                    out = f"KP(L={len(l_str)},len={len(vals)-2},a={vals[-2]})"
                                                    break
                            outcomes[k] = out
                        kinds = {v[0] for v in outcomes.values()}
                        if 'K' in kinds:
                            h0_s = "---" if halt_bit == 0 else h_act
                            h1_s = "---" if halt_bit == 1 else h_act
                            summary = " | ".join(f"k={k}:{outcomes[k]}" for k in [1,2,3,4,5,6,20])
                            print(f"  C1={c1_act} H={h0_s}{h1_s}: {summary}")
