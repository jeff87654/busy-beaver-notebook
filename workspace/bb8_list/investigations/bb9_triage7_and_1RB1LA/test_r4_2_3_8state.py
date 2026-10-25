import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl

tm = '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA1RB'
t = kl.tmpl(tm, 'R,B,P=-,u=1,s=10,d=1d+0,b=3b+1,S=-')

def parse_tr(tm_str):
    tr = {}
    for qi, row in enumerate(tm_str.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-':
                tr[(qi, c)] = (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return tr

tr_base = parse_tr(tm)

print("=== How [0, 0; 5], [0, 0; 6], [0, 0; 7] finish after the last E1 ===")
for a in [5, 6, 7]:
    w = kl.word(t, [0, 0], a, 0)
    tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
    pos, q = len(w), 1
    last_e = 0
    hist = []
    for st in range(1, 1000):
        c = tape.get(pos, 0)
        if q == 4:
            last_e = st
        lo, hi = min(min(tape.keys()), pos), max(max(tape.keys()), pos)
        s = ''.join(f"[{chr(65+q)}{tape.get(i,0)}]" if i == pos else str(tape.get(i,0)) for i in range(lo, hi+1))
        hist.append((st, s))
        W, d, nq = tr_base[(q, c)]
        if W: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d; q = nq
        if q == 1 and tape.get(pos, 0) == 0 and tape and pos > max(tape.keys()):
            lo = min(tape.keys())
            ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
            parts = ww.split('10')
            if len(parts) >= 2 and not any(set(x) - {'1'} for x in parts) and len(parts[-1]) == 1:
                vals = [len(x) for x in parts[:-1]]
                print(f"\n[0, 0; {a}] -> K({vals[:-1]}; {vals[-1]}) at step {st} (last E at {last_e}):")
                for h_st, h_s in hist[last_e-1:]:
                    print(f"  st {h_st:3d}: {h_s}")
                break
