import os, sys

H1_CODE  = "1RB1RE_1RC1RA_0LD1LE_1RE1LE_0RG0RF_---0LG_1LC1RA"
H2_CODE  = "1RB1RF_0LC1LD_1RD1LD_0RE0RG_1LB1RF_1RA1RD_---0LE"
C01_CODE = "1RB---_0RC0RA_0RD1LG_0LE1RC_1RF0LF_1LE1LD_0LD0LB"
C02_CODE = "1RB---_0RC0RA_0RD1LG_0LE1RC_1RF0LF_1LE1LD_0RD0LB"
H4_CODE  = "1RB0RE_1LC1RA_0LG1LD_0RB0RG_0RF---_1RC1LD_1LD0LB"
N2_CODE  = "1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA"
N2M_CODE = "1RB1RE_1LC0RA_1RF0RD_1LC0LE_1LD0LC_1RG0RE_0RB---"

def parse_tm(code):
    parts = code.strip().split("_")
    trans = {}
    for s_idx, p in enumerate(parts):
        st = chr(ord('A') + s_idx)
        for sym in (0, 1):
            chunk = p[3*sym:3*sym+3]
            if chunk == "---":
                trans[(st, sym)] = None
            else:
                trans[(st, sym)] = (int(chunk[0]), -1 if chunk[1] == 'L' else 1, chunk[2])
    return trans

print("=================================================================")
print("1. H1 EXACT TRACE OF E0:0 AND RARE PAIRS IN NATURAL & TEMPLATE RUNS")
print("=================================================================")

t_h1 = parse_tm(H1_CODE)
tape = {}
head = 0
st = 'A'
e00_events = []
for step in range(1, 200000):
    cur = tape.get(head, 0)
    slot = f"{st}{cur}"
    w, d, nxt = t_h1[(st, cur)]
    tape[head] = w
    head += d
    st = nxt
    nxt_sym = tape.get(head, 0)
    pair = f"{slot}:{nxt_sym}"
    if pair == "E0:0":
        mn, mx = min(tape.keys()), max(tape.keys())
        bits = "".join(str(tape.get(i, 0)) for i in range(max(mn, head-16), min(mx+1, head+16)))
        e00_events.append((step, head, mn, mx, bits))

print(f"H1 E0:0 events in 200,000 steps: {len(e00_events)}")
for ev in e00_events:
    print(f"  step={ev[0]}: head={ev[1]} range=[{ev[2]}..{ev[3]}] local_bits={ev[4]}")

# Check all 33 guard redirects of E0:0 on H1 from blank tape AND on exhaustion templates
STATES_8 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
ALL_ACTIONS = [None]
for w in (0, 1):
    for d in (-1, 1):
        for s in STATES_8:
            ALL_ACTIONS.append((w, d, s))

def run_blank(trans, max_steps=100000):
    tape = {}
    head = 0
    st = 'A'
    for step in range(1, max_steps + 1):
        cur = tape.get(head, 0)
        tr = trans.get((st, cur))
        if tr is None:
            return ("HALT", step, f"{st}{cur}")
        w, d, nxt = tr
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d
        st = nxt
    return ("TIMEOUT", max_steps, None)

e00_halts = []
for act in ALL_ACTIONS:
    t = dict(t_h1)
    old_w, old_d, old_nxt = t_h1[('E', 0)]
    t[('E', 0)] = (old_w, old_d, 'H')
    t[('H', 1)] = t_h1[(old_nxt, 1)]
    t[('H', 0)] = act
    r = run_blank(t, max_steps=50000)
    if r[0] == "HALT":
        e00_halts.append((act, r[1], r[2]))
print(f"H1 E0:0 guard redirects halting within 50,000 steps: {len(e00_halts)}/33")
for act, stp, sl in e00_halts:
    print(f"  act={act}: HALT at step {stp} ({sl})")

print("\n=================================================================")
print("2. N2 & N2m EXACT TRANSITION & GUARD-PAIR PROFILE")
print("=================================================================")
# Profile N2 and N2m across startup (steps 1..43), Round 1 countdown, and Round 1 exhaustion (step 66+)
for name, code in [("N2", N2_CODE), ("N2m", N2M_CODE)]:
    trans = parse_tm(code)
    tape = {}
    head = 0
    st = 'A'
    slots_by_phase = {"startup": set(), "engine": set(), "exhaust": set()}
    pairs_by_phase = {"startup": set(), "engine": set(), "exhaust": set()}
    first_slot_step = {}
    first_pair_step = {}
    for step in range(1, 5000):
        cur = tape.get(head, 0)
        slot = f"{st}{cur}"
        w, d, nxt = trans[(st, cur)]
        tape[head] = w
        head += d
        st = nxt
        nxt_sym = tape.get(head, 0)
        pair = f"{slot}:{nxt_sym}"
        if slot not in first_slot_step: first_slot_step[slot] = step
        if pair not in first_pair_step: first_pair_step[pair] = step
    print(f"\n[{name}] {code}")
    print("  First slot steps:", sorted(first_slot_step.items(), key=lambda x: x[1]))
    print("  First pair steps (>43):", [(k, v) for k, v in sorted(first_pair_step.items(), key=lambda x: x[1]) if v > 43])
