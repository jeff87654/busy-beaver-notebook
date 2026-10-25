import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl

def trace_tm(tm, tape_dict, pos, q, max_steps=500000, stop_fn=None):
    tr = {}
    for qi, row in enumerate(tm.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-':
                tr[(qi, c)] = (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    used = {}
    for st in range(1, max_steps + 1):
        c = tape_dict.get(pos, 0)
        slot = chr(65+q) + str(c)
        if slot not in used:
            used[slot] = st
        if (q, c) not in tr:
            return ('H', st, slot, used)
        W, d, nq = tr[(q, c)]
        if W:
            tape_dict[pos] = 1
        else:
            tape_dict.pop(pos, None)
        pos += d
        q = nq
        if stop_fn is not None:
            res = stop_fn(st, tape_dict, pos, q)
            if res is not None:
                return ('K', st, res, used)
    return ('T', max_steps, None, used)

# Check r4_2_rrFFr and r4_3_rrFFr from blank tape!
for name, tm in [
    ('r4_2_rrFFr', '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA0LE'),
    ('r4_3_rrFFr', '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA1RB'),
]:
    print(f"\n=== {name}: {tm} ===")
    t = kl.tmpl(tm, 'R,B,P=-,u=1,s=10,d=1d+0,b=3b+1,S=-')
    # Trace from blank tape for 30,000 steps and log first time each slot is used!
    res = trace_tm(tm, {}, 0, 0, max_steps=30000)
    print("Blank 30k first-use step per slot:", sorted(res[3].items(), key=lambda x: x[1]))

    # Now check K-events for D, B1, B2 (with y=0,1,2,3), B3 (with y=0,1,2,3), E(k=0,1,2)
    def make_s10(ds, a, b=0):
        w = kl.word(t, ds, a, b)
        tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
        return tape, len(w), 1 # state B = 1

    def check_s10(st, tape, pos, q):
        if q != 1 or tape.get(pos, 0) != 0:
            return None
        if not tape or pos <= max(tape.keys()):
            return None
        lo = min(tape.keys())
        ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
        parts = ww.split('10')
        if len(parts) < 2 or any(set(x) - {'1'} for x in parts):
            return None
        if len(parts[-1]) != 1:
            return None
        vals = [len(x) for x in parts[:-1]]
        return (vals[:-1], vals[-1])

    for ev_label, ds, a in [
        ('D [3;5]', [3], 5),
        ('D [1;5]', [1], 5),
        ('B1 [3,0;5]', [3, 0], 5),
        ('B1 [2,0;5]', [2, 0], 5),
        ('B1 [1,0;5]', [1, 0], 5),
        ('B2 [3,0,0;5]', [3, 0, 0], 5),
        ('B2 [2,0,0;5]', [2, 0, 0], 5),
        ('B2 [1,0,0;5]', [1, 0, 0], 5),
        ('B3 [3,0,0,0;5]', [3, 0, 0, 0], 5),
        ('B3 [1,0,0,0;5]', [1, 0, 0, 0], 5),
        ('E [0,0;3]', [0, 0], 3),
        ('E [0,0;0]', [0, 0], 0),
        ('E [0,0;1]', [0, 0], 1),
        ('E [0,0;2]', [0, 0], 2),
    ]:
        tape, pos, q = make_s10(ds, a, 0)
        kind, st, k, used = trace_tm(tm, tape, pos, q, max_steps=100000, stop_fn=check_s10)
        has_C1 = 'C1' in used
        has_E1 = 'E1' in used
        print(f"  {ev_label:16s} -> {kind} {str(k):30s} ({st:5d} st) | C1={has_C1!s:5s} E1={has_E1!s:5s} | slots={sorted(used.keys())}")
