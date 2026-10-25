import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape

for name, tm_str in [
    ("C3_1", "1RB---_1LC0LG_1RF1RD_0RF0LE_0LC1LB_1RA0RC_1LB0LE"),
    ("C3_2", "1RB---_1LC0LG_1RF1RD_0RF0LE_0LC1LB_1RA0RC_1RB0LE"),
    ("C3_3", "1RB0LE_1LC0LA_1RF1RD_0RF0LE_0LC1LB_1RG0RC_1RB---"),
]:
    trans = parse_tm(tm_str)
    # 1. Blank tape run for 50,000 steps
    used_blank = set()
    tape = {}; head = 0; state = 0
    for step in range(1, 50001):
        v = tape.get(head, 0)
        used_blank.add((state, v))
        w, d, ns = trans[(state, v)]
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
    all_slots = [(s, v) for s in range(7) for v in (0, 1)]
    unused_blank = [f"{chr(ord('A')+s)}{v}" for (s, v) in all_slots if (s, v) not in used_blank]
    
    # 2. Run on k_twos=0 rebuild for 50,000 steps
    used_rebuild = set()
    cfg = "101001010B[1]10001000101" if name != "C3_3" else "1010010C[0]10001000101"
    tape = {}; pos = 0; i = 0
    while i < len(cfg):
        if cfg[i].isalpha():
            state = ord(cfg[i]) - ord('A')
            if int(cfg[i+2]) == 1: tape[pos] = 1
            head = pos; pos += 1; i += 4
        else:
            if int(cfg[i]) == 1: tape[pos] = 1
            pos += 1; i += 1
    for step in range(1, 50001):
        v = tape.get(head, 0)
        used_rebuild.add((state, v))
        w, d, ns = trans[(state, v)]
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
    unused_rebuild = [f"{chr(ord('A')+s)}{v}" for (s, v) in all_slots if (s, v) not in used_rebuild]
    print(f"{name} ({tm_str}):")
    print(f"  Unused in blank tape 50k: {unused_blank}")
    print(f"  Unused in rebuild 50k:    {unused_rebuild}")
