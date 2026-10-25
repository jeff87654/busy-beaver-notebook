import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape
from test_c4_8state_general_k_M import make_exhaustion_tape

moves = ['---'] + [f"{w}{d}{s}" for w in (0, 1) for d in ('L', 'R') for s in 'ABCDEFGH']
c1_moves = [f"{w}{d}H" for w in (0, 1) for d in ('L', 'R')]

def sim_to_clean_k(tr, k, M, max_steps=2000):
    tape, head, state = make_exhaustion_tape(k, M)
    visited_h = set()
    for step in range(1, max_steps + 1):
        v = tape.get(head, 0)
        if state == 7:
            visited_h.add(v)
        t = tr.get((state, v))
        if t is None:
            return ('HALT', step - 1, len(tape), visited_h)
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
        if state == 4 and tape.get(head, 0) == 0 and (not tape or head <= min(tape.keys())):
            ft = format_tape(tape, head, state)
            m = re.match(r'^E\[0\](1+)((?:00(?:11)*)*)001$', ft)
            if m:
                b_new = len(m.group(1))
                ds = [len(p)//2 for p in m.group(2).split('00')[1:]]
                return ('CLEAN_K', step, b_new, ds, visited_h)
    return None

if __name__ == '__main__':
    for bname, g0 in [("C4_1", "0LD0RB"), ("C4_2", "1LC0RB")]:
        print(f"=== Scanning all 4,356 8-state extensions of {bname} ({g0}) ===")
        seen_patterns = {}
        for c1 in c1_moves:
            for h0 in moves:
                for h1 in moves:
                    tm_str = f"1RB0RG_1RC1RB_0RD{c1}_0LE0LD_0LF1LE_1RA1LF_{g0}_{h0}{h1}"
                    tr = parse_tm(tm_str)
                    r3 = sim_to_clean_k(tr, k=3, M=4, max_steps=1500)
                    if r3 and r3[0] == 'CLEAN_K':
                        # Test k=2, 3, 4, 5 with M=4, and k=3 with M=5
                        res_k = []
                        for kt in (2, 3, 4, 5):
                            rk = sim_to_clean_k(tr, k=kt, M=4, max_steps=2500)
                            res_k.append((kt, rk[1], rk[2], rk[3]) if rk and rk[0]=='CLEAN_K' else (kt, rk))
                        r_m5 = sim_to_clean_k(tr, k=3, M=5, max_steps=2500)
                        m5_sig = (r_m5[2], r_m5[3]) if r_m5 and r_m5[0]=='CLEAN_K' else r_m5
                        sig = (tuple((x[0], x[2], tuple(x[3])) if len(x)==4 else (x[0], None) for x in res_k),
                               (m5_sig[0], tuple(m5_sig[1])) if isinstance(m5_sig, tuple) and len(m5_sig)==2 else None)
                        if sig not in seen_patterns:
                            seen_patterns[sig] = []
                        seen_patterns[sig].append((f"C1={c1} H0={h0} H1={h1}", r3[4], res_k, m5_sig))
        print(f"Found {len(seen_patterns)} distinct CLEAN_K behavior classes for {bname}:")
        for sig, items in seen_patterns.items():
            label, vh, res_k, m5_sig = items[0]
            print(f"  Class ({len(items)} machines, e.g. {label}, H_used={vh}):")
            for x in res_k:
                print(f"    M=4, k={x[0]}: {x[1:]}")
            print(f"    M=5, k=3: {m5_sig}")
