import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

def parse_tm(tm_str):
    states = tm_str.strip().split('_')
    trans = {}
    for s_idx, s_str in enumerate(states):
        for sym in (0, 1):
            chunk = s_str[3*sym : 3*sym+3]
            if chunk == '---':
                trans[(s_idx, sym)] = None
            else:
                w = int(chunk[0])
                d = 1 if chunk[1] == 'R' else -1
                ns = ord(chunk[2]) - ord('A')
                trans[(s_idx, sym)] = (w, d, ns)
    return trans

def format_tape(tape, head, state):
    if not tape:
        return f"{chr(ord('A')+state)}[0]"
    mn = min(min(tape.keys()), head)
    mx = max(max(tape.keys()), head)
    # compress runs of 0s or 1s if long, or print raw if short
    chars = []
    for i in range(mn, mx + 1):
        v = tape.get(i, 0)
        if i == head:
            chars.append(f"{chr(ord('A')+state)}[{v}]")
        else:
            chars.append(str(v))
    return "".join(chars)

def run_and_dump_steps(name, tm_str, target_steps):
    trans = parse_tm(tm_str)
    tape = {}
    head = 0
    state = 0
    target_set = set(target_steps)
    max_s = max(target_steps)
    print(f"=== {name}: {tm_str} ===")
    for step in range(1, max_s + 1):
        v = tape.get(head, 0)
        t = trans.get((state, v))
        if t is None:
            print(f"  HALT at step {step-1} on {chr(ord('A')+state)}{v}: {format_tape(tape, head, state)}")
            break
        w, d, ns = t
        if w == 0:
            tape.pop(head, None)
        else:
            tape[head] = 1
        head += d
        state = ns
        if step in target_set:
            print(f"  step {step:6d}: {format_tape(tape, head, state)}")

# 1. Compare C1_bb7 and C1_new
run_and_dump_steps("C1_bb7", "1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF", [41, 77, 137, 245, 551, 2117])
run_and_dump_steps("C1_new", "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF", [33, 66, 122, 224, 518, 1951])

# 2. Dump C2_L1 and C2_R1 at kview steps
run_and_dump_steps("C2_L1", "1RB---_1LC1LE_1LD0LC_0RE0LA_0LF0RF_1RF1RG_1LB1RB", [26, 62, 114, 152, 240, 356, 706])
run_and_dump_steps("C2_R1", "1RB0LE_1RC1RA_1RD0RC_0LA0RG_1LE1LF_1RB1LB_1LB---", [20, 40, 76, 128, 166, 254, 370])

# 3. Dump C3_1 and C3_3 at kview steps
run_and_dump_steps("C3_1", "1RB---_1LC0LG_1RF1RD_0RF0LE_0LC1LB_1RA0RC_1LB0LE", [90, 290, 910, 1006, 1018, 1126, 2500])
run_and_dump_steps("C3_3", "1RB0LE_1LC0LA_1RF1RD_0RF0LE_0LC1LB_1RG0RC_1RB---", [50, 226, 798, 894, 906, 1014, 2388])

# 4. Dump C4_1 and C4_2 at kview steps
run_and_dump_steps("C4_1", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB", [3715, 3731, 3883, 3917, 4015, 4305])
run_and_dump_steps("C4_2", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB", [3775, 3791, 3943, 3977, 4075, 4365])
