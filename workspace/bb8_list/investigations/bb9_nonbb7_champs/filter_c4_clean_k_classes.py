import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape
from list_all_c4_clean_k import sim_to_clean_k, moves, c1_moves

if __name__ == '__main__':
    for bname, g0 in [("C4_1", "0LD0RB"), ("C4_2", "1LC0RB")]:
        print(f"=== Filtering 8-state extensions of {bname} ({g0}) that reach CLEAN_K at k=21, M=5 ===")
        good_21 = []
        for c1 in c1_moves:
            for h0 in moves:
                for h1 in moves:
                    tm_str = f"1RB0RG_1RC1RB_0RD{c1}_0LE0LD_0LF1LE_1RA1LF_{g0}_{h0}{h1}"
                    tr = parse_tm(tm_str)
                    # Quick check at k=3, M=4 first
                    r3 = sim_to_clean_k(tr, k=3, M=4, max_steps=1500)
                    if not (r3 and r3[0] == 'CLEAN_K'):
                        continue
                    # Check if M=5 appends 1 to ds at k=3
                    r3_m5 = sim_to_clean_k(tr, k=3, M=5, max_steps=1500)
                    if not (r3_m5 and r3_m5[0] == 'CLEAN_K' and r3_m5[3] == r3[3] + [1]):
                        continue
                    # Now test at k=21, M=4!
                    r21 = sim_to_clean_k(tr, k=21, M=4, max_steps=15000)
                    if r21 and r21[0] == 'CLEAN_K':
                        # Also test at k=4, 5, 6, 20, 22 with M=4!
                        r4 = sim_to_clean_k(tr, k=4, M=4, max_steps=3000)
                        r5 = sim_to_clean_k(tr, k=5, M=4, max_steps=3000)
                        r6 = sim_to_clean_k(tr, k=6, M=4, max_steps=3000)
                        r20 = sim_to_clean_k(tr, k=20, M=4, max_steps=15000)
                        good_21.append((f"C1={c1} H0={h0} H1={h1}", r21[4], r3[1:4],
                                        r4[1:4] if r4 and r4[0]=='CLEAN_K' else r4,
                                        r5[1:4] if r5 and r5[0]=='CLEAN_K' else r5,
                                        r6[1:4] if r6 and r6[0]=='CLEAN_K' else r6,
                                        r20[1:4] if r20 and r20[0]=='CLEAN_K' else r20,
                                        r21[1:4]))
        # Group by (r3, r4, r5, r6, r20, r21)
        by_sig = {}
        for item in good_21:
            sig = str(item[2:])
            by_sig.setdefault(sig, []).append(item)
        print(f"Found {len(good_21)} machines in {len(by_sig)} classes reaching CLEAN_K at k=21 (with M-extension):")
        for sig, items in by_sig.items():
            it = items[0]
            print(f"  [{len(items):2d} machines] {it[0]} (H_used={it[1]}):")
            print(f"    k= 3: {it[2]}")
            print(f"    k= 4: {it[3]}")
            print(f"    k= 5: {it[4]}")
            print(f"    k= 6: {it[5]}")
            print(f"    k=20: {it[6]}")
            print(f"    k=21: {it[7]}")
