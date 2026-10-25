import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl

def parse_word(w, t, B0):
    P, S, u, s = t['P'], t['S'], t['u'], t['s']
    if not (w.startswith(P) and w.endswith(S)) or len(w) < len(P)+len(S):
        return None
    body = w[len(P):len(w)-len(S)]
    parts = body.split(s)
    if len(parts) < 2:
        return None
    vals = []
    for p in parts[:-1]:
        if len(p) % len(u) != 0 or p != u * (len(p) // len(u)):
            return None
        r = len(p) // len(u)
        if r < t['be'] or (r - t['be']) % t['al'] != 0:
            return None
        vals.append((r - t['be']) // t['al'])
    bp = parts[-1]
    if len(bp) % len(u) != 0 or bp != u * (len(bp) // len(u)):
        return None
    br = len(bp) // len(u)
    if br < t['beB'] or (br - t['beB']) % t['alB'] != 0 or (br - t['beB']) // t['alB'] != B0:
        return None
    return (vals[:-1], vals[-1])

def run_event(tm, t, B0, ds, a, maxs=300000):
    mir = t['o'] == 'L'
    tr = {}
    for q, row in enumerate(tm.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-':
                d = 1 if x[1] == 'R' else -1
                tr[(q, c)] = (int(x[0]), -d if mir else d, ord(x[2]) - 65)
    w = kl.word(t, ds, a, B0)
    tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
    pos = len(w)
    Q = ord(t['q']) - 65
    q = Q
    used = set()
    for st in range(maxs):
        c = tape.get(pos, 0)
        if st > 0 and c == 0 and q == Q:
            ones = [i for i, v in tape.items() if v]
            if ones and pos > max(ones):
                lo = min(ones)
                ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
                k = parse_word(ww, t, B0)
                if k is not None:
                    return ('K', k, used, st)
        if (q, c) not in tr:
            return ('H', (chr(65+q), c), used, st)
        used.add(chr(65+q) + str(c))
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return ('T', None, used, maxs)

def trace_blank_used(tm, steps=2500):
    tr = {}
    for q, row in enumerate(tm.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-':
                tr[(q, c)] = (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    tape = {}
    pos = 0
    q = 0
    used = set()
    for st in range(steps):
        c = tape.get(pos, 0)
        if (q, c) not in tr:
            break
        used.add(chr(65+q) + str(c))
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return used

CANDIDATES = [
    ('r4_2_rrFFr', '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA0LE', 'R,B,P=-,u=1,s=10,d=1d+0,b=3b+1,S=-', 0,
     [('D', [3], 5), ('B1', [2, 0], 5), ('B2', [2, 0, 0], 5), ('E_k2_a3', [0, 0], 3), ('E_k2_a7', [0, 0], 7)]),
    ('r4_3_rrFFr', '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA1RB', 'R,B,P=-,u=1,s=10,d=1d+0,b=3b+1,S=-', 0,
     [('D', [3], 5), ('B1', [2, 0], 5), ('B2', [2, 0, 0], 5), ('E_k2_a3', [0, 0], 3), ('E_k2_a7', [0, 0], 7)]),
    ('r4_4_rFrL', '1RB0RD_0RC1RG_1RD1RC_1LD0LE_0RB1LF_0LC1LE_---1RA', 'L,E,P=-,u=1,s=10,d=1d+0,b=2b+1,S=10', 2,
     [('D', [3], 5), ('B1', [2, 0], 5), ('E_k2', [0, 0], 5), ('E_k0_a5', [], 5), ('E_k0_a7', [], 7)]),
    ('reb_E1_1', '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RA0RG_---0RB', 'L,E,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1,
     [('D', [3], 5), ('B1', [2, 0], 5), ('B2', [2, 0, 0], 5), ('E_k0', [], 5), ('E_k2', [0, 0], 5)]),
    ('reb_E1_2', '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RC0RG_---0RB', 'L,E,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1,
     [('D', [3], 5), ('B1', [2, 0], 5), ('B2', [2, 0, 0], 5), ('E_k0', [], 5), ('E_k2', [0, 0], 5)]),
    ('reb_E1_3', '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RC0RG_---0RB', 'L,E,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1,
     [('D', [3], 5), ('B1', [2, 0], 5), ('B2', [2, 0, 0], 5), ('E_k0', [], 5), ('E_k2', [0, 0], 5)]),
    ('reb_E2', '1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC', 'R,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1,
     [('D', [3], 5), ('B1', [2, 0], 5), ('B2', [2, 0, 0], 5), ('E_k0', [], 5), ('E_k2', [0, 0], 5)]),
    ('reb_F1', '1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA', 'L,B,P=01,u=1,s=0,d=1d+0,b=1b+0,S=0', 1,
     [('D', [3], 5), ('B1', [2, 0], 5), ('B2', [2, 0, 0], 5), ('E_k0', [], 5), ('E_k2', [0, 0], 5)]),
    ('multi_1', '1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF', 'R,C,P=-,u=11,s=0,d=1d+0,b=1b+0,S=-', 1,
     [('D', [3], 5), ('B1', [2, 0], 5), ('B2', [2, 0, 0], 5), ('E_k0', [], 5), ('E_k2', [0, 0], 5)]),
    ('w1loop_1', '1RB0RE_1RC1RA_0LD0LE_1RE0LE_0RF1LC_1LC1RG_0RB---', 'R,B,P=-,u=1,s=0,d=1d+1,b=1b+0,S=-', 1,
     [('D', [3], 5), ('B1', [2, 0], 5), ('B2', [2, 0, 0], 5), ('E_k0', [], 5), ('E_k2', [0, 0], 5)]),
]

for name, tm, t_str, B0, events in CANDIDATES:
    t = kl.tmpl(tm, t_str)
    res = {}
    for ev_name, ds, a in events:
        res[ev_name] = run_event(tm, t, B0, ds, a)
    d_b_used = set()
    e_used = set()
    for ev_name, (st, k, used, steps) in res.items():
        if ev_name.startswith('E'):
            e_used |= used
        else:
            d_b_used |= used
    blank_used = trace_blank_used(tm, 2000)
    e_only_vs_db = sorted(e_used - d_b_used)
    e_only_vs_all = sorted(e_used - d_b_used - blank_used)
    print(f"{name:12s} | D/B used ({len(d_b_used)}): {' '.join(sorted(d_b_used))} | E-only vs D/B: {e_only_vs_db} | E-only vs Blank+D/B: {e_only_vs_all}")
    for ev_name, (st, k, used, steps) in res.items():
        print(f"   {ev_name:10s}: {st} k={k} steps={steps} used={sorted(used)}")
