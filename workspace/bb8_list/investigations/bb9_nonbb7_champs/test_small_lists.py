import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

from test_exhaustion import parse_tm, format_tape

def run_from_config(name, tm_str, tape_str, max_steps=100000):
    # parse tape_str like "11101101B[0]" or "E[0]111110011001"
    trans = parse_tm(tm_str)
    tape = {}
    head = None
    state = None
    pos = 0
    i = 0
    while i < len(tape_str):
        if tape_str[i].isalpha():
            state = ord(tape_str[i]) - ord('A')
            assert tape_str[i+1] == '[' and tape_str[i+3] == ']'
            v = int(tape_str[i+2])
            if v == 1:
                tape[pos] = 1
            head = pos
            pos += 1
            i += 4
        else:
            v = int(tape_str[i])
            if v == 1:
                tape[pos] = 1
            pos += 1
            i += 1
    for step in range(1, max_steps + 1):
        v = tape.get(head, 0)
        t = trans.get((state, v))
        if t is None:
            print(f"[{name}] HALT at step {step-1} on {chr(ord('A')+state)}{v}, ones={len(tape)}: {format_tape(tape, head, state)}")
            return "HALT", step-1, len(tape), format_tape(tape, head, state)
        w, d, ns = t
        if w == 0:
            tape.pop(head, None)
        else:
            tape[head] = 1
        head += d
        state = ns
    print(f"[{name}] RUNNING at {max_steps}, ones={len(tape)}: {format_tape(tape, head, state)[:120]}")
    return "RUN", max_steps, len(tape), format_tape(tape, head, state)

print("--- Test 1: C1_bb7 vs C1_new on small lists ---")
# In C1_bb7 at step 2117:
# 111 01010101010101 101 101 101 101 101 101 101 101 101 101 101 101 0111001B[0]
# Notice: 111 (prefix) + (01)^7 (d_0 = 2 -> 3*2+1 = 7 copies of 01) + (101)^10 (ten 0-digits: 01 + separator 1 -> 101) + 101 101 0111001B[0]
# Let's test with 1 zero digit instead of 10, and d_0 = 0 or 1!
for k_zeros in [0, 1, 2]:
    cfg = "111" + "01" + ("101" * k_zeros) + "1011010111001B[0]"
    run_from_config(f"C1_bb7 (k={k_zeros})", "1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF", cfg, 200000)
    run_from_config(f"C1_new (k={k_zeros})", "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF", cfg, 200000)

print("\n--- Test 2: C4_1 and C4_2 on small lists ---")
# At step 3715 of C4_1:
# E[0]11111 + ("0011" * 20) + "001"
for k_ones in [0, 1, 2]:
    cfg = "E[0]11111" + ("0011" * k_ones) + "001"
    run_from_config(f"C4_1 (k={k_ones})", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB", cfg, 500000)
    run_from_config(f"C4_2 (k={k_ones})", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB", cfg, 500000)

print("\n--- Test 3: C3_1 and C3_3 on small lists ---")
# At step 1018 of C3_1:
# 10100C[1]110101010101 00 0010100 010100 010100 101
# Wait: look at step 910 of C3_1:
# 101001010B[1]10 00 10 00 1010 00 1010 00 1010 00 101
# Wait: u=10, s=00! So digits in step 910 are: 0 (empty), 1 (10), 2 (1010), 2 (1010), 2 (1010), and prefix on right is 101!
for k_twos in [0, 1]:
    cfg = "101001010B[1]10001000" + ("101000" * k_twos) + "101"
    run_from_config(f"C3_1 (k={k_twos})", "1RB---_1LC0LG_1RF1RD_0RF0LE_0LC1LB_1RA0RC_1LB0LE", cfg, 500000)
    cfg3 = "1010010C[0]100010" + ("001010" * k_twos) + "00101"
    run_from_config(f"C3_3 (k={k_twos})", "1RB0LE_1LC0LA_1RF1RD_0RF0LE_0LC1LB_1RG0RC_1RB---", cfg3, 500000)
