import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

HERE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_7state_fw1_redirects'
tsv = os.path.join(HERE, 'enum_rebE2_9.tsv')

e1_halts = []
e2_halts = []
by_redir_type = {}
state7_halts = []
state8_halts = []
state9_halts = []

with open(tsv, 'r') as f:
    header = f.readline()
    for line in f:
        parts = line.rstrip('\r\n').split('\t')
        if len(parts) < 7:
            continue
        redir, typ, tm, blank, e1_7, e1_9, e2_7 = parts
        by_redir_type[(redir, typ)] = by_redir_type.get((redir, typ), 0) + 1
        if typ in ('E1_HALT', 'E2_HALT'):
            rows = tm.split('_')
            if rows[7] == '------' and rows[8] == '------':
                n_st = 7
                state7_halts.append(parts)
            elif rows[8] == '------':
                n_st = 8
                state8_halts.append(parts)
            else:
                n_st = 9
                state9_halts.append(parts)
            if typ == 'E1_HALT':
                e1_halts.append((n_st, parts))
            else:
                e2_halts.append((n_st, parts))

print("=== Summary of enum_rebE2_9.tsv by (redir, type) ===")
for k, v in sorted(by_redir_type.items()):
    print(f"  {k[0]:10s} | {k[1]:10s}: {v}")

print(f"\nHalting leaves by state count: 7-state={len(state7_halts)}, 8-state={len(state8_halts)}, 9-state={len(state9_halts)}")
print(f"E1_HALT total={len(e1_halts)}, E2_HALT total={len(e2_halts)}")

if state7_halts:
    print("\n=== 7-STATE HALTERS FOUND! ===")
    for p in state7_halts[:20]:
        print("  ", "\t".join(p))

if state8_halts:
    print("\n=== 8-STATE HALTERS FOUND! ===")
    for p in state8_halts[:30]:
        print("  ", "\t".join(p))

if e2_halts:
    print("\n=== E2_HALT (ROUND-2 HALTERS) FOUND! ===")
    for n_st, p in e2_halts[:40]:
        print(f"  [{n_st}-state] " + "\t".join(p))

print("\n=== Sample E1_HALT by redir slot ===")
seen_redir = {}
for n_st, p in e1_halts:
    r = (p[0], n_st)
    if seen_redir.get(r, 0) < 8:
        seen_redir[r] = seen_redir.get(r, 0) + 1
        print(f"  [{n_st}-state {p[0]}] " + "\t".join(p[1:]))
