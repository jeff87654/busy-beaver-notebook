from inspect_nonper import parse_tm

def trace_early(tm_str, k=4, N=10, max_steps=600):
    tr = parse_tm(tm_str)
    tape = {}
    pos = 0
    for _ in range(2 * k - 1):
        tape[pos] = 1; pos += 1
        tape[pos] = 0; pos += 1
    for b in [1, 1, 0, 0, 1]:
        tape[pos] = b; pos += 1
    h = pos
    for b in [1, 1, 0, 0]:
        tape[pos] = b; pos += 1
    for _ in range(N):
        for b in [1, 1, 0, 0]:
            tape[pos] = b; pos += 1
    tape[pos] = 1
    q = 'C'
    min_h = h
    for step in range(1, max_steps + 1):
        b = tape.get(h, 0)
        act = tr[(q, b)]
        if act is None:
            print(f'  step {step}: HALT({q}{b}) at h={h}')
            return
        w, d, nxt = act
        tape[h] = w
        h += d
        q = nxt
        if h < min_h:
            min_h = h
            if h <= 2:
                lo = min(p for p, v in tape.items() if v == 1)
                s = ''.join(str(tape.get(p, 0)) for p in range(lo - 2, lo + 36))
                print(f'  step {step:4d}: q={q} h={h:3d} lo={lo:3d} tape={s}')

tms = [
    ('CS1 [3]', '1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LH0RB_0LE0LI_0RF---'),
    ('STD9 [16]', '1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1RA0RD'),
    ('STD9 [32]', '1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_0RA0RI'),
    ('STD9 [63]', '1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1RF1LG'),
    ('STD9 [64]', '1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---'),
    ('STD9 [72]', '1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_1RA0RE'),
]

for name, tm in tms:
    print(f'=== {name} (k=4) ===')
    trace_early(tm, k=4, N=10)
    print(f'=== {name} (k=5) ===')
    trace_early(tm, k=5, N=10)
