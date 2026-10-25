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
    tr = {}
    for qi, row in enumerate(tm.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-':
                tr[(qi, c)] = (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)

    def step_k(ds, a, max_steps=200000):
        w = kl.word(t, ds, a, 0)
        tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
        pos, q = len(w), 1
        for st in range(1, max_steps + 1):
            c = tape.get(pos, 0)
            if (q, c) not in tr:
                return ('HALT', st, chr(65+q) + str(c))
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
                    return ('K', st, vals[:-1], vals[-1])
        return ('TIMEOUT', max_steps, None)

    print("1. Check [3, 2, 2, 2, 0, 0; a] for a = 3, 7, 11:")
    for a in [3, 7, 11]:
        print(f"   a={a:2d} -> {step_k([3, 2, 2, 2, 0, 0], a)}")

    print("2. Check [3, 0, 0; a] for a = 3, 7, 11, 15, 19:")
    for a in [3, 7, 11, 15, 19]:
        print(f"   a={a:2d} -> {step_k([3, 0, 0], a)}")

    print("3. Check [W, z+1, y, 0, 0; a] -> [W, z; 3a + 3y + 11] across W, z, y, a:")
    ok = 0
    for W in [[], [3], [3, 2], [2, 1]]:
        for z in [0, 1, 2, 3]:
            for y in [1, 2, 3, 4]:
                for a in [0, 1, 2, 3, 5, 8]:
                    res = step_k(W + [z + 1, y, 0, 0], a)
                    exp_ds = W + [z]
                    exp_a = 3 * a + 3 * y + 11
                    assert res[0] == 'K' and res[2] == exp_ds and res[3] == exp_a, f"FAIL {W} {z} {y} {a}: {res} != {exp_ds};{exp_a}"
                    ok += 1
    print(f"   Verified {ok}/{ok} cases of [W, z+1, y, 0, 0; a] -> [W, z; 3a + 3y + 11]!")
