import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from analyze_1RB1LA_slots import VARIANTS, parse_tm, make_tape_F, is_F_config

def collect_contexts(tm_str, W, b, max_steps=100000):
    T = parse_tm(tm_str)
    tape, head, q = make_tape_F(W, b)
    ctxs = set()
    for step in range(1, max_steps + 1):
        c = tape.get(head, 0)
        # Record local tape window [head-3 .. head+3]
        win = tuple(tape.get(head + dc, 0) for dc in range(-3, 4))
        ctxs.add((q, c, win))
        tr = T.get((q, c))
        if tr is None: break
        w, d, nx = tr
        if w == 1: tape[head] = 1
        else: tape.pop(head, None)
        head += d; q = nx
        if is_F_config(tape, head, q) is not None:
            break
    return ctxs

tm = VARIANTS[0]
c_r1 = collect_contexts(tm, [2, 2], 0) | collect_contexts(tm, [1, 2], 1) | collect_contexts(tm, [2, 2], 2)
c_r3a = collect_contexts(tm, [0, 2], 2) | collect_contexts(tm, [0, 0, 2], 3) | collect_contexts(tm, [0, 1], 6)
c_r4 = collect_contexts(tm, [0], 2) | collect_contexts(tm, [0], 3)

only_r4 = c_r4 - (c_r1 | c_r3a)
print(f"Total 7-cell contexts in R1+R3A: {len(c_r1 | c_r3a)}, in R4: {len(c_r4)}")
print(f"7-cell contexts (q, c, tape[h-3..h+3]) in R4 but NOT in R1 or R3A(r>=1): {len(only_r4)}")
for q, c, win in sorted(only_r4):
    print(f"  slot={q}{c} win(-3..+3)={win} (left={win[2]}, cur={win[3]}, right={win[4]})")

# Also check 3-cell contexts (left1, cur, right1) and 5-cell contexts (left2..right2):
for radius in (1, 2, 3):
    s_13 = {(q, c, win[3-radius:3+radius+1]) for (q, c, win) in (c_r1 | c_r3a)}
    s_4 = {(q, c, win[3-radius:3+radius+1]) for (q, c, win) in c_r4}
    diff = s_4 - s_13
    print(f"Radius {radius} ({2*radius+1}-cell window) unique to R4: {len(diff)}")
    for item in sorted(diff):
        print("  ", item)
