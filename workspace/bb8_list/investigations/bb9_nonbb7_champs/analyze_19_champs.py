import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

CHAMPS = [
    # Family E & F from prompt
    ("FamE", "1RB0RA_1LC1RF_1RE0LD_0LC0LE_1RA---_1RD0LG_0RF0RG", "R,E,P=1,u=10,s=1,d=1d+1,b=2b+2,S=-"),
    ("FamF", "1RB1LC_0LA0LD_1LA1LF_1RE0RB_1RF1LE_1RG0RC_0RF---", "R,A,P=10,u=01,s=10,d=1d+0,b=1b+0,S=-"),
    # Group C1 (BB7 champ + new sibling)
    ("C1_bb7", "1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF", "R,B,P=11,u=10,s=1,d=3d+1,b=3b+2,S=111001"),
    ("C1_new", "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF", "R,B,P=11,u=10,s=1,d=3d+1,b=3b+2,S=111001"),
    # Group C2 (u=0011, s=01)
    ("C2_L1", "1RB---_1LC1LE_1LD0LC_0RE0LA_0LF0RF_1RF1RG_1LB1RB", "L,D,P=1,u=0011,s=01,d=1d+0,b=1b+0,S=000000001"),
    ("C2_L2", "1RB---_1LC1LE_1LD0LC_0RE0LA_1LB0RF_1RF1RG_1LB1RB", "L,D,P=1,u=0011,s=01,d=1d+0,b=1b+0,S=00000001"),
    ("C2_R1", "1RB0LE_1RC1RA_1RD0RC_0LA0RG_1LE1LF_1RB1LB_1LB---", "R,D,P=1,u=0011,s=01,d=1d+0,b=1b+0,S=00000001"),
    ("C2_R2", "1RB0LE_1RC1RA_1RD0RC_0LA1RG_1LE1LF_1RB1LB_0RC---", "R,D,P=1,u=0011,s=01,d=1d+0,b=1b+0,S=00000001"),
    # Group C3 (L, B/C, P=101, u=10, s=00)
    ("C3_1", "1RB---_1LC0LG_1RF1RD_0RF0LE_0LC1LB_1RA0RC_1LB0LE", "L,B,P=101,u=10,s=00,d=1d+0,b=2b+1,S=1"),
    ("C3_2", "1RB---_1LC0LG_1RF1RD_0RF0LE_0LC1LB_1RA0RC_1RB0LE", "L,B,P=101,u=10,s=00,d=1d+0,b=2b+1,S=1"),
    ("C3_3", "1RB0LE_1LC0LA_1RF1RD_0RF0LE_0LC1LB_1RG0RC_1RB---", "L,C,P=101,u=10,s=00,d=1d+0,b=2b+1,S=11"),
    # Group C4 (L, E, P=100, u=11, s=00)
    ("C4_1", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB", "L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1"),
    ("C4_2", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB", "L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1"),
    # Group C5 (R1 0b+3 constant slope)
    ("C5_1", "1RB0RB_1RC1RG_1LD---_1RA1LE_0RF0LE_1LC0RF_0LD1RD", "L,E,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
    ("C5_2", "1RB0RB_1RC1RG_1LD---_1RA1LE_0RF0LE_1LC0RF_0LF1RD", "L,E,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
    ("C5_3", "1RB1LD_1RC0RF_1LA---_0RE0LD_1LC0RE_0LA1RG_0LA1RA", "L,D,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
    ("C5_4", "1RB1LD_1RC0RF_1LA---_0RE0LD_1LC0RE_0RA1RG_0LA1RA", "L,D,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
    ("C5_5", "1RB1LD_1RC0RF_1LA---_0RE0LD_1LC0RE_1LF1RG_0LA1RA", "L,D,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
    ("C5_6", "1RB1LD_1RC0RF_1LA---_0RE0LD_1LC0RE_1LF1RG_0LE1RA", "L,D,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
]

def parse_tm(code):
    states = code.split('_')
    trans = {}
    undef = []
    for s_idx, s_str in enumerate(states):
        s_ch = chr(ord('A') + s_idx)
        for sym in (0, 1):
            sub = s_str[3*sym:3*sym+3]
            if sub == '---':
                trans[(s_ch, sym)] = None
                undef.append(f"{s_ch}{sym}")
            else:
                w = int(sub[0])
                d = 1 if sub[1] == 'R' else -1
                ns = sub[2]
                trans[(s_ch, sym)] = (w, d, ns)
    return trans, undef

def run_tm(code, max_steps=200000):
    trans, undef = parse_tm(code)
    tape = {}
    head = 0
    state = 'A'
    min_p, max_p = 0, 0
    used = set()
    for step in range(max_steps):
        val = tape.get(head, 0)
        tr = trans.get((state, val))
        if tr is None:
            return "HALT", step, state, val, head, min_p, max_p, tape, used, undef
        used.add(f"{state}{val}")
        w, d, state = tr
        tape[head] = w
        head += d
        if head < min_p: min_p = head
        if head > max_p: max_p = head
    return "RUN", max_steps, state, tape.get(head, 0), head, min_p, max_p, tape, used, undef

for tag, code, tmpl in CHAMPS:
    status, step, st, val, hd, min_p, max_p, tape, used, undef = run_tm(code, 500000)
    ones = sum(tape.values())
    all_slots = {f"{chr(ord('A')+i)}{b}" for i in range(7) for b in (0, 1)}
    unused = sorted(all_slots - used - set(undef))
    print(f"{tag:8s} | {code} | undef={undef} unused_500k={unused} | {status}@{step} span={max_p-min_p+1} ones={ones}")
