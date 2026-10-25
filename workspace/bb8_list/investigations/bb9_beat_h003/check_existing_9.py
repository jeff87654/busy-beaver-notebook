import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from collections import Counter, defaultdict

def parse_cell(s):
    m = re.match(r'k(\d+)=([A-Za-z\*]+)\(([^)]+)\)\@(\d+)', s)
    if not m:
        return None
    k = int(m.group(1))
    kind = m.group(2)
    inner = m.group(3)
    step = int(m.group(4))
    info = {'k': k, 'kind': kind, 'step': step}
    if kind in ('K', 'K*'):
        parts = inner.split(',')
        info['dL'] = int(parts[0][2:])
        info['I'] = int(parts[1][1:])
        info['a'] = int(parts[2][1:])
        info['d1'] = int(parts[3][1:])
        info['d2'] = int(parts[4])
        info['c'] = int(parts[5][1:])
    elif kind in ('H', 'H*'):
        parts = inner.split(',')
        info['slot'] = parts[0]
        info['c'] = int(parts[1][1:])
    else:
        info['c'] = int(inner[1:])
    return info

def load_tsv(path):
    rows = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            tag, tm, rest = line.split('\t')
            left_part, r20_part = rest.split('|')
            cells = {}
            for tok in left_part.strip().split():
                c = parse_cell(tok)
                if c: cells[c['k']] = c
            c20 = parse_cell(r20_part.strip())
            if c20: cells[20] = c20
            rows.append((tag, tm, cells))
    return rows

MOD2 = 1024
MOD = 3 * 9 * 5 * MOD2 # 138240, divisible by 2^10 * 3^3 * 5
a_cur = 1
for _ in range(30):
    a_cur = ((pow(3, 3 * a_cur + 2, 2 * MOD) * 5 - 3) // 2) % MOD
A_MOD_BY_I = {a_cur % 2: a_cur}
a_next = ((pow(3, 3 * a_cur + 2, 2 * MOD) * 5 - 3) // 2) % MOD
A_MOD_BY_I[a_next % 2] = a_next
THREE_A_MOD = {0: (3 * A_MOD_BY_I[0]) % MOD, 1: (3 * A_MOD_BY_I[1]) % MOD}

def detect_period_rule_gen(cells, k_start=1, max_P=8):
    for P in range(1, max_P + 1):
        if k_start + P > 9: continue
        ok = True
        for k in range(k_start, 10 - P):
            k1, k2 = cells[k]['kind'][0], cells[k + P]['kind'][0]
            if k1 != k2 or k1 == 'T':
                ok = False
                break
        if not ok:
            continue
        k20_ref = k_start + ((20 - k_start) % P)
        if cells[20]['kind'][0] != cells[k20_ref]['kind'][0]:
            continue
        rules = {}
        for k0 in range(k_start, k_start + P):
            kind0 = cells[k0]['kind']
            if kind0[0] == 'H':
                rules[k0 % P] = ('H', kind0, cells[k0]['slot'])
            elif kind0[0] == 'K':
                if k0 + P <= 9:
                    step_dL = cells[k0 + P]['dL'] - cells[k0]['dL']
                    step_I = (cells[k0 + P]['I'] - cells[k0]['I']) % 2
                    test_ks = [k for k in range(k0, 10, P)]
                    if 20 % P == k0 % P:
                        test_ks.append(20)
                    for tk in test_ks:
                        m = (tk - k0) // P
                        exp_dL = cells[k0]['dL'] + m * step_dL
                        exp_I = (cells[k0]['I'] + m * step_I) % 2
                        if cells[tk]['dL'] != exp_dL or cells[tk]['I'] != exp_I:
                            ok = False
                            break
                    if not ok:
                        break
                    rules[k0 % P] = ('K', kind0, k0, cells[k0]['dL'], step_dL, cells[k0]['I'], step_I)
                elif 20 % P == k0 % P and (20 - k0) // P > 0:
                    m20 = (20 - k0) // P
                    if (cells[20]['dL'] - cells[k0]['dL']) % m20 != 0:
                        ok = False
                        break
                    step_dL = (cells[20]['dL'] - cells[k0]['dL']) // m20
                    # For step_I, if m20 is odd we can infer it
                    if m20 % 2 == 1:
                        step_I = (cells[20]['I'] - cells[k0]['I']) % 2
                    else:
                        step_I = 0
                        if cells[20]['I'] != cells[k0]['I']:
                            ok = False
                            break
                    rules[k0 % P] = ('K', kind0, k0, cells[k0]['dL'], step_dL, cells[k0]['I'], step_I)
                else:
                    ok = False
                    break
            else:
                ok = False
                break
        if ok:
            return P, rules
    return None, None

def trace_blank_tape_rounds(P, rules, k1=20, I1=1, max_rounds=50):
    k_mod = k1 % MOD
    I_cur = I1
    history = []
    seen = set()
    for r in range(1, max_rounds + 1):
        res_class = k_mod % P
        rule = rules[res_class]
        if rule[0] == 'H':
            history.append((r, k_mod, I_cur, rule[1], rule[2]))
            return 'HALT', r, history
        _, kind0, k0, dL0, step_dL, I0, step_I = rule
        if (k_mod, I_cur) in seen:
            history.append((r, k_mod, I_cur, 'LOOP', ''))
            return 'LOOP', r, history
        seen.add((k_mod, I_cur))
        N_mod = (THREE_A_MOD[I_cur] + 1 - k_mod) % MOD
        # Compute m = (k_mod - k0) / P mod MOD (requires P | MOD)
        m = (k_mod - k0) // P
        dL = dL0 + m * step_dL
        I_evenN = (I0 + m * step_I) % 2
        k_next = (N_mod + dL) % MOD
        I_next = (I_evenN + N_mod) % 2
        history.append((r, k_mod, I_cur, kind0, f"->(k%{P*2}={k_next%(P*2)},I={I_next})"))
        k_mod, I_cur = k_next, I_next
    return 'MAX', max_rounds, history

for label, path in [
    ("champ_231", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ231_9.tsv"),
    ("champ_232", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ232_9.tsv"),
]:
    rows = load_tsv(path)
    print(f"=== {label} ({len(rows)} rows) ===")
    for k_start in [1, 2, 3, 4]:
        found = []
        for tag, tm, cells in rows:
            if tag != "MIXED_KH": continue
            P, rules = detect_period_rule_gen(cells, k_start=k_start, max_P=6)
            if P is not None and any(v[0] == 'H' for v in rules.values()) and any(v[0] == 'K' for v in rules.values()):
                status, r_end, hist = trace_blank_tape_rounds(P, rules)
                if status == 'HALT' and r_end >= 3:
                    found.append((r_end, P, tm, hist))
        print(f"  k_start={k_start}: {len(found)} halters with R >= 3 (max R = {max([x[0] for x in found], default=0)})")
        for r_end, P, tm, hist in sorted(found, key=lambda x: -x[0])[:10]:
            if r_end >= 4:
                print(f"    R={r_end} P={P} {tm} {hist}")
    # Also check how many MIXED_KH were NOT matched by any period P <= 6 for k_start=3
    unmatched = []
    for tag, tm, cells in rows:
        if tag != "MIXED_KH": continue
        if cells[20]['kind'][0] != 'K': continue # must survive Round 1 (k1=20)!
        P, rules = detect_period_rule_gen(cells, k_start=2, max_P=6)
        if P is None:
            unmatched.append((tm, cells))
    print(f"  MIXED_KH surviving R1 (k20=K/K*) not matched by P<=6 from k=2: {len(unmatched)}")
    for tm, cells in unmatched[:25]:
        pf = ",".join(f"{cells[k]['kind']}" for k in range(1, 10))
        print(f"    {tm} | {pf} | k20={cells[20]['kind']}(dL={cells[20].get('dL')},I={cells[20].get('I')},c={cells[20].get('c')})")
