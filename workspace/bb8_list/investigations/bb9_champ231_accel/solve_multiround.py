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
    summary = ""
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith('#summary'):
                summary = line
                continue
            tag, tm, rest = line.split('\t')
            left_part, r20_part = rest.split('|')
            cells = {}
            for tok in left_part.strip().split():
                c = parse_cell(tok)
                if c: cells[c['k']] = c
            c20 = parse_cell(r20_part.strip())
            if c20: cells[20] = c20
            rows.append((tag, tm, cells))
    return rows, summary

# Compute exact 2-adic fixed 2-cycle of a -> (5 * 3^(3a+2) - 3) // 2 mod 1024
MOD2 = 1024
MOD = 3 * MOD2 # 3072
a_cur = 1
for _ in range(20):
    a_cur = ((pow(3, 3 * a_cur + 2, 2 * MOD2) * 5 - 3) // 2) % MOD2
A_MOD_BY_I = {a_cur % 2: a_cur}
a_next = ((pow(3, 3 * a_cur + 2, 2 * MOD2) * 5 - 3) // 2) % MOD2
A_MOD_BY_I[a_next % 2] = a_next
print(f"2-adic contraction fixed points mod {MOD2}: I=1 -> A == {A_MOD_BY_I[1]} (mod {MOD2}), I=0 -> A == {A_MOD_BY_I[0]} (mod {MOD2})")
THREE_A_MOD = {0: (3 * A_MOD_BY_I[0]) % MOD, 1: (3 * A_MOD_BY_I[1]) % MOD}
print(f"3*A mod {MOD}: I=1 -> {THREE_A_MOD[1]}, I=0 -> {THREE_A_MOD[0]}")

def detect_period_rule(cells):
    # Check if k=2..9 follows a periodic K/H rule with period P in {1, 2, 3, 4}
    for P in [1, 2, 3, 4]:
        ok = True
        for k in range(2, 10 - P):
            k1, k2 = cells[k]['kind'][0], cells[k + P]['kind'][0]
            if k1 != k2 or k1 == 'T':
                ok = False
                break
        if not ok:
            continue
        # Also check k=20 matches 2 + ((20 - 2) % P)
        k20_ref = 2 + ((20 - 2) % P)
        if cells[20]['kind'][0] != cells[k20_ref]['kind'][0]:
            continue
        # For each K residue class r_idx in 2 .. 2 + P - 1, check linearity of dL and I
        rules = {}
        for k0 in range(2, 2 + P):
            kind0 = cells[k0]['kind']
            if kind0[0] == 'H':
                rules[k0 % P] = ('H', kind0, cells[k0]['slot'])
            elif kind0[0] == 'K':
                if k0 + P <= 9:
                    step_dL = cells[k0 + P]['dL'] - cells[k0]['dL']
                    step_I = (cells[k0 + P]['I'] - cells[k0]['I']) % 2
                    # Verify across all k0 + m*P <= 9 and k=20 (if 20 == k0 mod P)
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
                else:
                    ok = False
                    break
        if ok:
            return P, rules
    return None, None

def trace_blank_tape_rounds(P, rules, k1=20, I1=1, max_rounds=30):
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
        # rule is ('K', kind0, k0, dL0, step_dL, I0, step_I)
        _, kind0, k0, dL0, step_dL, I0, step_I = rule
        if (k_mod, I_cur) in seen:
            history.append((r, k_mod, I_cur, 'LOOP', ''))
            return 'LOOP', r, history
        seen.add((k_mod, I_cur))
        # Compute N_r mod MOD:
        N_mod = (THREE_A_MOD[I_cur] + 1 - k_mod) % MOD
        m = ((k_mod - k0) // P)
        dL = dL0 + m * step_dL
        I_evenN = (I0 + m * step_I) % 2
        k_next = (N_mod + dL) % MOD
        I_next = (I_evenN + N_mod) % 2
        history.append((r, k_mod, I_cur, kind0, f"->(k%24={k_next%24},I={I_next})"))
        k_mod, I_cur = k_next, I_next
    return 'MAX', max_rounds, history

if __name__ == '__main__':
    for label, path in [
        ("champ_231", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ231_9.tsv"),
        ("champ_232", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ232_9.tsv"),
    ]:
        rows, summary = load_tsv(path)
        print(f"\n==================================================================")
        print(f"{label}: {len(rows)} rows | {summary}")
        print(f"==================================================================")
        tag_counts = Counter(r[0] for r in rows)
        print("Tag counts:", dict(tag_counts))

        no_t_mixed = sum(1 for tag, _, c in rows if tag == "MIXED_KH" and all(c[k]['kind'] != 'T' for k in range(1, 10)))
        print(f"MIXED_KH with ZERO timeouts on k=1..9: {no_t_mixed} / {tag_counts['MIXED_KH']}")

        pat_counter = Counter()
        pat_ex = {}
        multiround_halters = defaultdict(list)

        for tag, tm, cells in rows:
            if tag == "MIXED_KH":
                pf = ",".join(cells[k]['kind'] for k in range(1, 10))
                k20k = cells[20]['kind']
                pat_counter[(pf, k20k)] += 1
                if (pf, k20k) not in pat_ex:
                    pat_ex[(pf, k20k)] = (tm, cells)

            P, rules = detect_period_rule(cells)
            if P is not None and any(v[0] == 'H' for v in rules.values()) and any(v[0] == 'K' for v in rules.values()):
                status, r_end, hist = trace_blank_tape_rounds(P, rules)
                pf = ",".join(cells[k]['kind'] for k in range(1, 10))
                multiround_halters[(status, r_end, P, pf)].append((tm, cells, hist))

        print(f"\nPeriodic MIXED_KH multi-round blank-tape analysis (k1=20, I1=1):")
        for (status, r_end, P, pf), lst in sorted(multiround_halters.items(), key=lambda x: (-x[0][1] if x[0][0]=='HALT' else 0, -len(x[1]))):
            ex_tm, ex_cells, ex_hist = lst[0]
            h_str = " ; ".join(f"R{r}:(k%24={km%24},I={ic})->{act}{ extra}" for r, km, ic, act, extra in ex_hist)
            print(f"  [{status:4s} @ R{r_end:2d}] P={P} cnt={len(lst):3d} | {pf:26s} | {h_str} | ex={ex_tm}")

        print(f"\nTop 30 MIXED_KH (k1..k9 | k20) patterns:")
        for (pf, k20k), cnt in pat_counter.most_common(30):
            ex_tm, ex_cells = pat_ex[(pf, k20k)]
            c_str = ",".join(str(ex_cells[k]['c']) for k in range(1, 10))
            s_str = ",".join(str(ex_cells[k]['step']) for k in range(1, 6))
            print(f"  cnt={cnt:4d} | {pf:26s} | k20={k20k:2s} | c=[{c_str}] | s1..5=[{s_str}] | {ex_tm}")
