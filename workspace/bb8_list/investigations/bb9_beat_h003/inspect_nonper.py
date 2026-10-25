def parse_tm(s):
    tr = {}
    for q_idx, part in enumerate(s.split('_')):
        q = chr(ord('A') + q_idx)
        for b in (0, 1):
            sub = part[3*b:3*b+3]
            if sub == '---':
                tr[(q, b)] = None
            else:
                tr[(q, b)] = (int(sub[0]), 1 if sub[1] == 'R' else -1, sub[2])
    return tr

def sim_pure(tm_str, k, N, max_steps=200000):
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
    hi_init = pos
    q = 'C'
    for step in range(1, max_steps + 1):
        b = tape.get(h, 0)
        act = tr[(q, b)]
        if act is None:
            return f'HALT({q}{b}) at step {step}, h={h}, hi_init={hi_init}'
        w, d, nxt = act
        tape[h] = w
        h += d
        q = nxt
        # check if K-form at E0
        if q == 'E' and tape.get(h, 0) == 0:
            lo = min(p for p, v in tape.items() if v == 1)
            hi = max(p for p, v in tape.items() if v == 1)
            if h == lo - 1 and tape.get(h+1,0)==1 and tape.get(h+2,0)==0 and tape.get(h+3,0)==0:
                # check if rest is 1^{2a} 00 (1^{2d} 00)^s 1
                p = h + 4
                runs = []
                ok = True
                while p <= hi - 1:
                    ones = 0
                    while p <= hi - 1 and tape.get(p, 0) == 1:
                        ones += 1; p += 1
                    if ones == 0 or ones % 2 != 0:
                        ok = False; break
                    if tape.get(p, 0) != 0 or tape.get(p+1, 0) != 0:
                        ok = False; break
                    p += 2
                    runs.append(ones // 2)
                if ok and p == hi and tape.get(hi, 0) == 1 and len(runs) >= 2:
                    return f'K-FORM at step {step}: a={runs[0]}, k_len={len(runs)-1} (dL={len(runs)-1-N}), runs[:5]={runs[:5]}, runs[-3:]={runs[-3:]}, hi={hi} vs hi_init={hi_init}'
    return f'TIMEOUT at {max_steps}, h={h}, hi_init={hi_init}'

tms = [
    ('CS1 [3]', '1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LH0RB_0LE0LI_0RF---'),
    ('STD9 [16]', '1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1RA0RD'),
    ('STD9 [32]', '1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_0RA0RI'),
    ('STD9 [63]', '1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1RF1LG'),
    ('STD9 [64]', '1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---'),
    ('STD9 [72]', '1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_1RA0RE'),
]

for name, tm in tms:
    print(f'=== {name}: {tm} ===')
    for k in [4, 5, 6, 7, 8]:
        for N in [10, 14]:
            print(f'  k={k}, N={N}: {sim_pure(tm, k, N)}')
