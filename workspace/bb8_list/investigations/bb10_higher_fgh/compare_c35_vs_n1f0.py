# Compare why c35 does H: [1^(n+1) | a] -> [2, 1^(2a+4), 0, 1^n | 6] without hitting E0,
# whereas n1f0 hits E0 (or halts at I0/J0) at [0*2, 1^12 | r; t=0]!

def parse_tm(s):
    tr = {}
    for q, part in enumerate(s.split('_')):
        for b in (0, 1):
            cell = part[3*b:3*b+3]
            if cell == '---':
                tr[(q, b)] = None
            else:
                tr[(q, b)] = (int(cell[0]), 1 if cell[1] == 'R' else -1, ord(cell[2]) - ord('A'))
    return tr

def D(m):
    return [1, 0] * m + [1]

def run_trace(tm_str, tape_bits, head_pos, init_q, max_steps=5000):
    tr = parse_tm(tm_str)
    tape = {}
    for i, b in enumerate(tape_bits):
        if b: tape[i] = 1
    pos = head_pos
    q = ord(init_q) - ord('A')
    used = set()
    events = []
    for step in range(max_steps):
        b = tape.get(pos, 0)
        slot = f"{chr(ord('A')+q)}{b}"
        if slot in ('E0', 'I0', 'I1', 'J0', 'J1', 'H0', 'H1'):
            if not events or events[-1][1] != slot:
                left_ctx = [tape.get(pos - k, 0) for k in range(6, 0, -1)]
                right_ctx = [tape.get(pos + k, 0) for k in range(0, 6)]
                events.append((step, slot, pos, left_ctx, right_ctx))
        used.add(slot)
        t = tr.get((q, b))
        if t is None:
            return f"HALT_{slot}", step, used, events
        w, d, nq = t
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d
        q = nq
    return "MAX", max_steps, used, events

# 1. Test c35 (n1_REC) on [1^5 | a=4]: D(1)^5 ++ D(0) ++ D(4) in state G reading 0
n1_rec = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_0LJ0LI_---0LC"
bits_c35 = D(1)*5 + D(0) + D(4)
res, st, used, ev = run_trace(n1_rec, bits_c35, len(bits_c35), 'G', 5000)
print("c35 (n1_REC) on [1^5 | 4]:", res, "steps:", st, "used:", sorted(used))
for e in ev[:15]:
    print("  event:", e)

# 2. Test n1f0_Per1 on [0*2, 1^5; m=1; r=5; t=0]: D(0)^2 ++ D(1)^5 ++ D(1) ++ (10)^5 11 1001 in state B reading 0
n1f0_per1 = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI0LH_---0LC"
bits_n1f0 = D(0)*2 + D(1)*5 + D(1) + [1,0]*5 + [1,1] + [1,0,0,1]
res2, st2, used2, ev2 = run_trace(n1f0_per1, bits_n1f0, len(bits_n1f0), 'B', 5000)
print("\nn1f0_Per1 on [0*2, 1^5; 1; 5; 0]:", res2, "steps:", st2, "used:", sorted(used2))
for e in ev2[:15]:
    print("  event:", e)

# 3. What if n1f0 has NO 0*2 prefix (i.e. pure 1^6; m=1; r=5; t=0)?
bits_n1f0_pure = D(1)*5 + D(1) + [1,0]*5 + [1,1] + [1,0,0,1]
res3, st3, used3, ev3 = run_trace(n1f0_per1, bits_n1f0_pure, len(bits_n1f0_pure), 'B', 5000)
print("\nn1f0_Per1 on pure [1^5; 1; 5; 0] (no 0*2):", res3, "steps:", st3, "used:", sorted(used3))
for e in ev3[:15]:
    print("  event:", e)
