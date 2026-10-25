import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

VARIANTS = [
    "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_0RH0RF_---0LB",
    "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_0RH0RF_---0LD",
    "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_0RH0RF_---1LE",
    "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_1RH0RF_---0LA",
    "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_1RH0RF_---0LG",
    "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_1RH0RF_---1RB",
    "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RH0LC_0LD0RG_0RH0RF_---0LB",
]

def parse_tm(tm_str):
    parts = tm_str.split('_')
    T = {}
    for q_idx, p in enumerate(parts):
        q = chr(ord('A') + q_idx)
        for c in (0, 1):
            sub = p[3*c:3*c+3]
            if sub == '---':
                T[(q, c)] = None
            else:
                w = int(sub[0])
                d = 1 if sub[1] == 'R' else -1
                nx = sub[2]
                T[(q, c)] = (w, d, nx)
    return T

def make_tape_F(W, b):
    # Tape (left to right): ... (10)^d_n 00 ... (10)^d_1 00 (10)^a 00 (10)^(2b+2) D>
    # Wait: in rules_fam.py:
    # left stream (nearest the head first) = (0101)^(b+1), then for each digit d of W (nearest first): 0 0 (01)^d
    # Let's check left-to-right tape order:
    # Since nearest head first is (0,1,0,1)^(b+1) then 0,0,(0,1)^d, moving left from head reads 0, then 1, then 0, then 1...
    # Which means left-to-right on tape is (1,0)^d_n 0,0 ... (1,0)^a 0,0 (1,0)^(2b+2) [head D on 0]
    bits = []
    for d in reversed(W):
        bits.extend([1, 0] * d)
        bits.extend([0, 0])
    bits.extend([1, 0] * (2 * b + 2))
    tape = {i: bit for i, bit in enumerate(bits) if bit}
    head = len(bits)
    return tape, head, 'D'

def is_F_config(tape, head, q):
    if q != 'D': return None
    if tape.get(head, 0) != 0: return None
    # Check nothing to the right of head
    if any(k >= head for k in tape): return None
    if not tape: return None
    lo = min(tape.keys())
    # Wait: leading zeros on left don't matter, we decode from head-1 leftwards!
    # Moving left from head-1:
    pos = head - 1
    # Read (0,1) units
    def read_01_run(p):
        cnt = 0
        while p >= lo - 2:
            if tape.get(p, 0) == 0 and tape.get(p-1, 0) == 1:
                cnt += 1
                p -= 2
            else:
                break
        return cnt, p
    b_units, pos = read_01_run(pos)
    if b_units < 2 or b_units % 2 != 0:
        return None
    b = (b_units - 2) // 2
    W = []
    while pos >= lo:
        if tape.get(pos, 0) == 0 and tape.get(pos-1, 0) == 0:
            pos -= 2
            d, pos = read_01_run(pos)
            W.append(d)
        else:
            return None
    return (W, b)

def trace_rule(tm_str, W, b, max_steps=100000):
    T = parse_tm(tm_str)
    tape, head, q = make_tape_F(W, b)
    used_slots = []
    used_set = set()
    for step in range(1, max_steps + 1):
        c = tape.get(head, 0)
        slot = f"{q}{c}"
        if slot not in used_set:
            used_set.add(slot)
        used_slots.append(slot)
        tr = T.get((q, c))
        if tr is None:
            return 'HALT', step, used_set, used_slots
        w, d, nx = tr
        if w == 1:
            tape[head] = 1
        else:
            tape.pop(head, None)
        head += d
        q = nx
        res = is_F_config(tape, head, q)
        if res is not None:
            return res, step, used_set, used_slots
    return 'TIMEOUT', max_steps, used_set, used_slots

for idx, tm in enumerate(VARIANTS):
    print(f"\n=== Variant {idx}: {tm} ===")
    _, _, s_init, _ = trace_rule(tm, [], 0, max_steps=350) # wait: let's also trace blank tape to init!
    # Trace blank tape until first F config
    T = parse_tm(tm)
    tape, head, q = {}, 0, 'A'
    init_slots = set()
    for st in range(1, 1000):
        c = tape.get(head, 0)
        init_slots.add(f"{q}{c}")
        w, d, nx = T[(q, c)]
        if w: tape[head] = 1
        else: tape.pop(head, None)
        head += d; q = nx
        res = is_F_config(tape, head, q)
        if res == ([2, 2], 0):
            print(f"  Blank -> F([2,2],0) at step {st}: slots = {sorted(init_slots)}")
            break

    res_r1, st_r1, slots_r1, _ = trace_rule(tm, [2, 2], 0)
    res_r3a1, st_r3a1, slots_r3a1, _ = trace_rule(tm, [0, 2], 2)
    res_r3a2, st_r3a2, slots_r3a2, _ = trace_rule(tm, [0, 0, 2], 3)
    res_r3b, st_r3b, slots_r3b, _ = trace_rule(tm, [0, 0, 2], 1)
    res_r4, st_r4, slots_r4, seq_r4 = trace_rule(tm, [0], 2)
    print(f"  R1 ([2,2],0)->{res_r1} ({st_r1} st): {sorted(slots_r1)}")
    print(f"  R3A j=1 ([0,2],2)->{res_r3a1} ({st_r3a1} st): {sorted(slots_r3a1)}")
    print(f"  R3A j=2 ([0,0,2],3)->{res_r3a2} ({st_r3a2} st): {sorted(slots_r3a2)}")
    print(f"  R3B j=2,b=1 ([0,0,2],1)->{res_r3b} ({st_r3b} st): {sorted(slots_r3b)}")
    print(f"  R4 ([0],2)->{res_r4} ({st_r4} st): {sorted(slots_r4)}")
    only_r4 = slots_r4 - (slots_r1 | slots_r3a1 | slots_r3a2)
    print(f"  Slots in R4 but NOT in R1/R3A: {sorted(only_r4)}")
