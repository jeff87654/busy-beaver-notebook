import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl

for name, tm in [
    ('r4_2_rrFFr', '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA0LE'),
    ('r4_3_rrFFr', '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA1RB'),
]:
    print(f"\n================ {name}: {tm} ================")
    t = kl.tmpl(tm, 'R,B,P=-,u=1,s=10,d=1d+0,b=3b+1,S=-')

    def run_k_chain(ds, a, max_k=20):
        print(f"  Start chain: {ds}; {a}")
        for kstep in range(1, max_k + 1):
            tr = {}
            for qi, row in enumerate(tm.split('_')):
                for c in range(2):
                    x = row[3*c:3*c+3]
                    if x[0] != '-':
                        tr[(qi, c)] = (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
            w = kl.word(t, ds, a, 0)
            tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
            pos, q = len(w), 1
            hit = None
            for st in range(1, 2000000):
                c = tape.get(pos, 0)
                if (q, c) not in tr:
                    hit = ('HALT', st, chr(65+q) + str(c))
                    break
                W, d, nq = tr[(q, c)]
                if W: tape[pos] = 1
                else: tape.pop(pos, None)
                pos += d; q = nq
                if q == 1 and tape.get(pos, 0) == 0 and tape and pos > max(tape.keys()):
                    lo = min(tape.keys())
                    ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
                    parts = ww.split('10')
                    if len(parts) >= 2 and not any(set(x) - {'1'} for x in parts) and len(parts[-1]) == 1:
                        vals = [len(x) for x in parts[:-1]]
                        hit = ('K', st, vals[:-1], vals[-1])
                        break
            if hit is None:
                print(f"    step {kstep}: TIMEOUT at {ds}; {a}")
                break
            elif hit[0] == 'HALT':
                print(f"    step {kstep}: HALT at {hit[2]} in {hit[1]} TM steps!")
                break
            else:
                _, st, ds, a = hit
                print(f"    step {kstep}: -> {ds}; {a} (a mod 4 = {a%4}) in {st} TM steps")

    # Test 1: [3, 1, 1; 2] (which has the exact same parity/mod-4 structure as [3, 1, 147; 2]!)
    run_k_chain([3, 1, 1], 2)
    # Test 2: [3, 2, 2, 2, 1, 1; 2] (which has the exact same parity/mod-4 structure as [3, 2, 2, 2, 1, 147; 2], i.e. N=4!)
    run_k_chain([3, 2, 2, 2, 1, 1], 2)
