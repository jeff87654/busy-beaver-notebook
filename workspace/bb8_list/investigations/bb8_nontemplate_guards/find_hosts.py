import os

PROMPT_STRINGS = {
    "P_F5": "1RB0LD_1RC1RA_1LD0LA_1LE1LF_0LC0LG_---1LC_1RF0LE",
    "P_F89": "1RB1LC_1RC1RB_0RD0LC_1LE1RA_1LF0LD_0LA---_1RE0LF",
    "P_H1": "1RB0LF_1RC0LD_1LD1RA_1LA1LE_0LC---_1RG1LF_0RE0RC",
    "P_c01": "1RB1LF_0RC1RA_1LD0LC_1LA1RD_0RF0LE_1LG1LF_0LE---",
}

def sim_blank(m, max_steps=100000):
    rows = m.split("_")
    T = {}
    for q, r in enumerate(rows):
        for s in (0, 1):
            t = r[3*s:3*s+3]
            if t == "---":
                T[(q, s)] = None
            else:
                T[(q, s)] = (int(t[0]), 1 if t[1] == "R" else -1, ord(t[2]) - 65)
    tape = {}
    p = 0
    q = 0
    used = set()
    for step in range(1, max_steps + 1):
        s = tape.get(p, 0)
        used.add((q, s))
        tr = T.get((q, s))
        if tr is None:
            return f"HALT at step {step} in {chr(65+q)}{s}, span={len(tape)}, used={len(used)}"
        tape[p] = tr[0]
        p += tr[1]
        q = tr[2]
    return f"RUN >={max_steps}, span={len(tape)}, ones={sum(tape.values())}, used={len(used)}"

print("=== Simulating Prompt Strings ===")
for k, m in PROMPT_STRINGS.items():
    print(f"  {k}: {m} -> {sim_blank(m)}")
