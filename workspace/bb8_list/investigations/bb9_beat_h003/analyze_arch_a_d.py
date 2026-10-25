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

def load_tsv(path, has_fam=True):
    rows = []
    summary = ""
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith('#summary'):
                summary = line
                continue
            parts = line.split('\t')
            if has_fam:
                if len(parts) < 5: continue
                tag, fam, tm, ec_s, rest = parts[0], parts[1], parts[2], parts[3], parts[4]
            else:
                if len(parts) < 3: continue
                tag, tm, rest = parts[0], parts[1], parts[2]
                fam, ec_s = "STD9", "ec=11"
            if '|' not in rest: continue
            left_part, r20_part = rest.split('|')
            cells = {}
            for tok in left_part.strip().split():
                c = parse_cell(tok)
                if c: cells[c['k']] = c
            c20 = parse_cell(r20_part.strip())
            if c20: cells[20] = c20
            if len(cells) == 10:
                rows.append((tag, fam, tm, ec_s, cells))
    return rows, summary

# Use exact p-adic modulus with 3^25, 2^20, and 5^5 so division by P in {1..12} up to 25 rounds never loses p-adic precision!
MOD = (3**25) * (2**20) * (5**5)
a_cur = 1
for _ in range(40):
    a_cur = ((pow(3, 3 * a_cur + 2, 2 * MOD) * 5 - 3) // 2) % MOD
A_MOD_BY_I = {a_cur % 2: a_cur}
a_next = ((pow(3, 3 * a_cur + 2, 2 * MOD) * 5 - 3) // 2) % MOD
A_MOD_BY_I[a_next % 2] = a_next
THREE_A_MOD = {0: (3 * A_MOD_BY_I[0]) % MOD, 1: (3 * A_MOD_BY_I[1]) % MOD}

def detect_period_rule_gen(cells, k_start=2, max_P=6):
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

def trace_blank_tape_rounds(P, rules, k1=20, I1=1, max_rounds=25):
    k_mod = k1 % MOD
    I_cur = I1
    history = []
    seen = set()
    for r in range(1, max_rounds + 1):
        res_class = k_mod % P
        rule = rules[res_class]
        if rule[0] == 'H':
            history.append((r, k_mod % 24, I_cur, rule[1], rule[2]))
            return 'HALT', r, history
        _, kind0, k0, dL0, step_dL, I0, step_I = rule
        # Check loop modulo (P * 24)
        state_key = (k_mod % (P * 72), I_cur)
        if state_key in seen and step_dL % P == 0:
            history.append((r, k_mod % 24, I_cur, 'LOOP', ''))
            return 'LOOP', r, history
        seen.add(state_key)
        N_mod = (THREE_A_MOD[I_cur] + 1 - k_mod)
        m = (k_mod - k0) // P
        dL = dL0 + m * step_dL
        I_evenN = (I0 + m * step_I) % 2
        k_next = (N_mod + dL) % MOD
        I_next = (I_evenN + N_mod) % 2
        history.append((r, k_mod % 24, I_cur, kind0, f"->(k%12={k_next%12},I={I_next})"))
        k_mod, I_cur = k_next, I_next
    return 'MAX', max_rounds, history

for label, path, has_fam in [
    ("search_arch_a_d", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\search_arch_a_d.tsv", True),
    ("accel_champ231_9", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ231_9.tsv", False),
    ("accel_champ232_9", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ232_9.tsv", False),
]:
    rows, summary = load_tsv(path, has_fam=has_fam)
    print(f"\n==================================================================")
    print(f"{label}: {len(rows)} rows | {summary}")
    print(f"==================================================================")
    multiround_halters = defaultdict(list)
    for tag, fam, tm, ec_s, cells in rows:
        if tag != "MIXED_KH": continue
        for k_start in [1, 2, 3, 4]:
            P, rules = detect_period_rule_gen(cells, k_start=k_start, max_P=6)
            if P is not None and any(v[0] == 'H' for v in rules.values()) and any(v[0] == 'K' for v in rules.values()):
                status, r_end, hist = trace_blank_tape_rounds(P, rules)
                if status == 'HALT' and r_end >= 3:
                    pf = ",".join(cells[k]['kind'] for k in range(1, 10))
                    multiround_halters[(status, r_end, P, fam, pf)].append((tm, cells, hist))
                break

    for (status, r_end, P, fam, pf), lst in sorted(multiround_halters.items(), key=lambda x: (-x[0][1], -len(x[1]))):
        ex_tm, ex_cells, ex_hist = lst[0]
        h_str = " ; ".join(f"R{r}:(k%24={km},I={ic})->{act}{extra}" for r, km, ic, act, extra in ex_hist[:8])
        print(f"  [{status:4s} @ R{r_end:2d}] P={P} cnt={len(lst):3d} {fam:20s} | {pf:26s} | {h_str} | {ex_tm}")
