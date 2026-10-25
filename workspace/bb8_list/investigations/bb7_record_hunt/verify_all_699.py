import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle

rows = []
with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_record_hunt\audit_out.tsv', encoding='utf-8') as f:
    hdr = f.readline().rstrip('\n').split('\t')
    for line in f:
        parts = line.rstrip('\n').split('\t')
        rows.append(dict(zip(hdr, parts)))

# Check if any row halted during the 8M-step trace
halted_in_trace = [r for r in rows if 'HALT@' in r['last_K']]
print(f"Halted in 8M-step trace: {len(halted_in_trace)}")
for r in halted_in_trace:
    print(" ", r['grade'], r['machine'], r['last_K'])

# Check if any row with patL == KKKKKKKKKKKK has small last_a + last_b at the end of trace
small_ab = [r for r in rows if r['patL'] == 'KKKKKKKKKKKK' and 'H' in r['patS']]
print(f"patL=K...K with H in patS: {len(small_ab)}")
for r in small_ab:
    # check max index of H in patS
    max_h = r['patS'].rfind('H')
    print(f"  {r['grade']:10s} {r['machine']} max_H_b={max_h:2d} max_n={r['max_n']:2s} last_K={r['last_K']}")
