import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl

tm = '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA1RB'
t = kl.tmpl(tm, 'R,B,P=-,u=1,s=10,d=1d+0,b=3b+1,S=-')

def trace_one(ds, a, max_steps=50000):
    tr = {}
    for qi, row in enumerate(tm.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-':
                tr[(qi, c)] = (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    w = kl.word(t, ds, a, 0)
    tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
    pos, q = len(w), 1
    used = set()
    for st in range(1, max_steps + 1):
        c = tape.get(pos, 0)
        slot = chr(65+q) + str(c)
        used.add(slot)
        if (q, c) not in tr:
            return ('H', slot, used)
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
                return ('K', (vals[:-1], vals[-1]), used)
    return ('T', None, used)

print("=== [0; a] for a = 0..7 ===")
for a in range(8):
    kind, k, used = trace_one([0], a)
    print(f"  [0; {a}] -> {kind} {k} | C1={'C1' in used} E1={'E1' in used}")

print("\n=== [; a] for a = 0..7 ===")
for a in range(8):
    kind, k, used = trace_one([], a)
    print(f"  [; {a}] -> {kind} {k} | C1={'C1' in used} E1={'E1' in used}")

def reduce_symbolic(ds, a_mod4):
    ds = list(ds)
    steps = []
    for _ in range(200):
        steps.append((list(ds), a_mod4))
        if len(ds) == 1 and ds[0] == 0:
            return ('E1', a_mod4, steps)
        elif len(ds) >= 2 and ds[-1] == 0 and ds[-2] == 0:
            if len(ds) == 2:
                return ('E2', a_mod4, steps)
            elif len(ds) == 3:
                y = ds[0]
                return ('E2', (a_mod4 + y + 2) % 4, steps)
            else:
                y = ds[-3]
                z_plus_1 = ds[-4]
                assert z_plus_1 >= 1
                a_new = (3 * a_mod4 + 3 * y + 11) % 4
                ds = ds[:-4] + [z_plus_1 - 1]
                a_mod4 = a_new
                continue
        elif len(ds) >= 2 and ds[-1] == 0:
            y_plus_1 = ds[-2]
            assert y_plus_1 >= 1
            ds = ds[:-2] + [y_plus_1 - 1, 2 if (a_mod4 % 2 == 0) else 1]
            a_mod4 = 2
            continue
        else:
            d = ds[-1]
            if len(ds) == 1:
                a_1 = a_mod4 if (d % 2 == 0) else (3 * a_mod4 + 1) % 4
                ds = [0]
                a_mod4 = a_1
            else:
                y = ds[-2]
                if y == 0:
                    a_1 = a_mod4 if (d % 2 == 0) else (3 * a_mod4 + 1) % 4
                    ds[-1] = 0
                    a_mod4 = a_1
                else:
                    parity = (a_mod4 + d) % 2
                    a_end = 2 if parity == 0 else 3
                    ds[-2] = 0
                    ds[-1] = 0
                    a_mod4 = a_end
    return ('LOOP', a_mod4, steps)

print("\n=== Symbolic reduction of [3, 2^N, 1; 14] and [3, 2^N, 2; 2] ===")
for N in range(1, 10):
    for tail, a0 in [(1, 14), (1, 2), (2, 2)]:
        ds = [3] + [2]*N + [tail]
        res, m_mod4, trace = reduce_symbolic(ds, a0 % 4)
        print(f"N={N:2d} [3, 2^{N}, {tail}; {a0:2d}] -> {res}(M == {m_mod4} mod 4) in {len(trace)} steps")
