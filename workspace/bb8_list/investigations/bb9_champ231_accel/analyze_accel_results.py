import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from collections import Counter, defaultdict

def parse_cell(s):
    # e.g. k1=K(L8,I1,a0,d0,0,c5)@68638 or k3=H(I1,c5)@67181 or k3=T(c12)@500000
    m = re.match(r'k(\d+)=([A-Za-z\*]+)\(([^)]+)\)\@(\d+)', s)
    if not m:
        return None
    k = int(m.group(1))
    kind = m.group(2)
    inner = m.group(3)
    step = int(m.group(4))
    info = {'k': k, 'kind': kind, 'step': step}
    if kind in ('K', 'K*'):
        # L8,I1,a0,d0,0,c5
        parts = inner.split(',')
        info['L'] = int(parts[0][1:])
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

for label, path in [
    ("champ_231", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ231_9.tsv"),
    ("champ_232", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ232_9.tsv"),
]:
    rows, summary = load_tsv(path)
    print(f"==================================================================")
    print(f"{label}: {len(rows)} saved rows | {summary}")
    print(f"==================================================================")
    tag_counts = Counter(r[0] for r in rows)
    print("Tag counts:", dict(tag_counts))

    # Count how many MIXED_KH and CLEAN_K rows have 0 timeouts across k=1..9
    no_t_mixed = 0
    pat_counter = Counter()
    mixed_by_pat = defaultdict(list)
    cascade_halt = []

    for tag, tm, cells in rows:
        pat = "".join(cells[k]['kind'][0] for k in range(1, 10))
        pat_full = ",".join(cells[k]['kind'] for k in range(1, 10))
        if tag == "MIXED_KH":
            if 'T' not in pat:
                no_t_mixed += 1
            pat_counter[(pat_full, cells[20]['kind'])] += 1
            mixed_by_pat[(pat_full, cells[20]['kind'])].append((tm, cells))
        if tag == "CASCADE" or (tag == "MIXED_KH" and any(cells[k]['c'] >= 10 for k in range(1, 10))):
            if any(cells[k]['kind'] in ('H', 'H*') for k in list(range(1, 10)) + [20]):
                cascade_halt.append((tag, tm, cells))

    print(f"MIXED_KH with ZERO timeouts on k=1..9: {no_t_mixed} / {tag_counts['MIXED_KH']}")
    print("\nTop 25 MIXED_KH (k1..k9 | k20) patterns:")
    for (pf, k20k), cnt in pat_counter.most_common(25):
        ex_tm, ex_cells = mixed_by_pat[(pf, k20k)][0]
        c_str = ",".join(str(ex_cells[k]['c']) for k in range(1, 10))
        s_str = ",".join(str(ex_cells[k]['step']) for k in range(1, 6))
        print(f"  count={cnt:4d} | {pf:26s} | k20={k20k:2s} | clears=[{c_str}] | steps1..5=[{s_str}] | ex={ex_tm}")

    print(f"\nCascade + Halt candidates: {len(cascade_halt)}")
    cas_pat_counter = Counter()
    cas_examples = {}
    for tag, tm, cells in cascade_halt:
        pf = ",".join(cells[k]['kind'] for k in range(1, 10))
        c_seq = tuple(cells[k]['c'] for k in range(1, 7))
        key = (tag, pf, cells[20]['kind'], c_seq)
        cas_pat_counter[key] += 1
        if key not in cas_examples:
            cas_examples[key] = (tm, cells)
    for (tag, pf, k20k, c_seq), cnt in cas_pat_counter.most_common(20):
        ex_tm, ex_cells = cas_examples[(tag, pf, k20k, c_seq)]
        print(f"  [{tag:8s}] cnt={cnt:3d} | {pf:22s} | k20={k20k:2s} | c1..6={list(c_seq)} | ex={ex_tm}")
