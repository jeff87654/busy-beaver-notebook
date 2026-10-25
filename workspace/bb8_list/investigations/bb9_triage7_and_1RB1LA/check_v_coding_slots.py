import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

def run_kview_and_used(tm, t, B0, ds, a, maxs=300000):
    evs = kl.run(tm, ds, a, B0, steps=maxs, nchg=0, maxl=50000, T=t, pall=1)
    ev1 = ('END',)
    stop_step = 5000
    for e in evs[1:]:
        if e[0] == 'H' or (e[0] == 'K' and e[4] == B0):
            ev1 = e
            stop_step = e[1]
            break
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
    q = ord(t['q']) - 65
    used = set()
    for st in range(stop_step):
        c = tape.get(pos, 0)
        if (q, c) not in tr:
            break
        used.add(chr(65+q) + str(c))
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return (ev1, used)

V_CANDIDATES = [
    ('reb_E1_1', '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RA0RG_---0RB', 'L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1),
    ('reb_E1_2', '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RC0RG_---0RB', 'L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1),
    ('reb_E1_3', '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RC0RG_---0RB', 'L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1),
    ('reb_E1_4', '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RD0RG_---0RB', 'L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1),
    ('reb_E1_5', '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RD0RG_---0RB', 'L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1),
    ('reb_E1_6', '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RE0RG_---0RB', 'L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1),
    ('reb_E1_7', '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RF0RG_---0RB', 'L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1),
    ('reb_E1_8', '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RF0RG_---0RB', 'L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1),
    ('reb_E1_9', '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RG0RG_---0RB', 'L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1),
    ('reb_E2', '1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC', 'L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', 1),
    ('multi_1', '1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF', 'R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1', 1),
]

for name, tm, t_str, B0 in V_CANDIDATES:
    t = kl.tmpl(tm, t_str)
    z = 0 if '1d+1' in t_str else 1
    events = [('D', [3], 5), ('B1', [3, z], 5), ('B2', [3, z, z], 5), ('E_k0', [], 5), ('E_k2', [z, z], 5)]
    res = {}
    for ev_name, ds, a in events:
        res[ev_name] = run_kview_and_used(tm, t, B0, ds, a)
    d_b_used = set()
    e_used = set()
    for ev_name, (ev, used) in res.items():
        if ev_name.startswith('E'):
            e_used |= used
        else:
            d_b_used |= used
    e_only = sorted(e_used - d_b_used)
    print(f"{name:10s} | D/B used ({len(d_b_used)}): {' '.join(sorted(d_b_used))} | E-only vs D/B: {e_only}")
    for ev_name, (ev, used) in res.items():
        print(f"   {ev_name:6s}: {ev} | used={sorted(used)}")
