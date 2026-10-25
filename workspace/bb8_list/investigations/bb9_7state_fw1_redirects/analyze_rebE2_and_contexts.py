import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

def parse_tm(tm, mir=False):
    tr = {}
    for q, row in enumerate(tm.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-':
                d = 1 if x[1] == 'R' else -1
                tr[(q, c)] = (int(x[0]), -d if mir else d, ord(x[2]) - 65)
    return tr

def format_tape_window(tape, pos, r=6):
    left = "".join(str(tape.get(pos + dc, 0)) for dc in range(-r, 0))
    cur = str(tape.get(pos, 0))
    right = "".join(str(tape.get(pos + dc, 0)) for dc in range(1, r + 1))
    return f"{left} [{cur}] {right}"

def format_full_tape(tape, pos, q):
    if not tape:
        return f"[{chr(65+q)}0]"
    mn = min(min(tape.keys()), pos)
    mx = max(max(tape.keys()), pos)
    out = []
    for i in range(mn, mx + 1):
        b = str(tape.get(i, 0))
        if i == pos:
            out.append(f"[{chr(65+q)}{b}]")
        else:
            out.append(b)
    return "".join(out)

def trace_blank(tm, max_steps, target_slot=None):
    tr = parse_tm(tm, mir=False)
    tape = {}
    pos = 0
    q = 0
    ctxs = set()
    hits = []
    for step in range(1, max_steps + 1):
        c = tape.get(pos, 0)
        slot = chr(65 + q) + str(c)
        win = tuple(tape.get(pos + dc, 0) for dc in range(-4, 5))
        ctxs.add((slot, win))
        if target_slot and slot == target_slot:
            hits.append((step, slot, format_tape_window(tape, pos, 6), format_full_tape(tape, pos, q)))
        if (q, c) not in tr:
            break
        w, d, nq = tr[(q, c)]
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d
        q = nq
    return ctxs, hits

def trace_k_event(tm, t_str, B0, ds, a, maxs=300000, target_slot=None):
    t = kl.tmpl(tm, t_str)
    evs = kl.run(tm, ds, a, B0, steps=maxs, nchg=0, maxl=50000, T=t, pall=1)
    ev1 = ('END',)
    stop_step = maxs
    for e in evs[1:]:
        if e[0] == 'H' or (e[0] == 'K' and e[4] == B0):
            ev1 = e
            stop_step = e[1]
            break
    # Note: in kl.py, if t['o'] == 'L', kl.word constructs the word from left-to-right in K-coordinates
    # which corresponds to mirrored TM execution. Wait: to match actual unmirrored TM coordinates,
    # if mir=True, left/right in win are reversed compared to real tape!
    # Let's convert to REAL (unmirrored) tape coordinates!
    mir = (t['o'] == 'L')
    tr = parse_tm(tm, mir=False)
    w = kl.word(t, ds, a, B0)
    tape = {}
    if not mir:
        for i, ch in enumerate(w):
            if ch == '1': tape[i] = 1
        pos = len(w)
    else:
        for i, ch in enumerate(w):
            if ch == '1': tape[-i] = 1
        pos = -len(w)
    q = ord(t['q']) - 65
    ctxs = set()
    hits = []
    for step in range(1, stop_step + 1):
        c = tape.get(pos, 0)
        slot = chr(65 + q) + str(c)
        win = tuple(tape.get(pos + dc, 0) for dc in range(-4, 5))
        ctxs.add((slot, win))
        if target_slot and slot == target_slot:
            hits.append((step, slot, format_tape_window(tape, pos, 6), format_full_tape(tape, pos, q)))
        if (q, c) not in tr:
            break
        W_bit, d, nq = tr[(q, c)]
        if W_bit: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d
        q = nq
    return ev1, ctxs, hits

print("="*80)
print("PART 1: DETAILED A0 TRACE ON reb_E2")
print("="*80)
tm_rebE2 = "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC"
t_rebE2 = "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"

c_init_E2, hits_init = trace_blank(tm_rebE2, 415, target_slot="A0")
print(f"Blank tape up to step 415 (K(5, 2^5; 3; 1)): {len(hits_init)} hits on A0:")
for step, slot, win_str, full_str in hits_init:
    print(f"  step {step:4d}: win={win_str} | full={full_str}")

_, hits_blank_more = trace_blank(tm_rebE2, 50000, target_slot="A0")
print(f"Blank tape up to step 50000: {len(hits_blank_more)} hits on A0 (steps: {[h[0] for h in hits_blank_more]})")

print("\nTracing E(1^k; a) on reb_E2 for k=0,1,2,3 and a=1,3,5,7,9:")
for k in [0, 1, 2, 3, 6]:
    for a in [1, 3, 5, 7]:
        ev, _, hits = trace_k_event(tm_rebE2, t_rebE2, 1, [1]*k, a, target_slot="A0")
        print(f"  E(1^{k}; a={a}) -> {ev}: {len(hits)} hits on A0:")
        for step, slot, win_str, full_str in hits[:5]:
            print(f"    step {step:4d}: win={win_str} | full={full_str}")

print("\n" + "="*80)
print("PART 2: LOCAL CONTEXT ANALYSIS (r = 0, 1, 2, 3, 4) FOR ALL 4 FAMILIES")
print("="*80)

MACHINES = [
    ("reb_E2", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC", "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 415, 1, [3, 5, 7]),
    ("reb_E1_1", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RA0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1493, 1, [3, 5, 7]),
    ("reb_E1_2", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RC0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1500, 1, [3, 5, 7]),
    ("reb_E1_3", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RC0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1500, 1, [3, 5, 7]),
    ("reb_E1_4", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RD0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1500, 1, [3, 5, 7]),
    ("reb_E1_5", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RD0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1500, 1, [3, 5, 7]),
    ("reb_E1_6", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RE0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1500, 1, [3, 5, 7]),
    ("reb_E1_7", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RF0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1500, 1, [3, 5, 7]),
    ("reb_E1_8", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RF0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1500, 1, [3, 5, 7]),
    ("reb_E1_9", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RG0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1500, 1, [3, 5, 7]),
    ("multi_1", "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF", "R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1", 1, 1848, 0, [1, 4, 10]),
    ("w1loop_1", "1RB0RE_1RC1RA_0LD0LE_1RE0LE_0RF1LC_1LC1RG_0RB---", "L,F,P=1,u=10,s=0,d=2d+0,b=2b+1,S=-", 1, 392, 0, [1, 4, 10]),
]

for name, tm, t_str, B0, init_steps, z_digit, a_vals in MACHINES:
    c_init, _ = trace_blank(tm, init_steps)
    c_db = set()
    v1 = z_digit + (2 if z_digit == 1 else 1)
    v2 = z_digit + (4 if z_digit == 1 else 2)
    for ds in [[v1], [v2], [v1, v1], [v1, z_digit], [v2, z_digit], [v1, z_digit, z_digit], [v1, z_digit, z_digit, z_digit]]:
        for a in a_vals:
            _, ctx, _ = trace_k_event(tm, t_str, B0, ds, a)
            c_db |= ctx
    c_e_common = None
    c_e_union = set()
    for k in [0, 2, 3]:
        for a in a_vals[1:]:
            _, ctx, _ = trace_k_event(tm, t_str, B0, [z_digit]*k, a)
            c_e_union |= ctx
            if c_e_common is None:
                c_e_common = set(ctx)
            else:
                c_e_common &= ctx
    print(f"\n--- {name}: {tm} ---")
    for r in [0, 1, 2, 3, 4]:
        s_init = {(sl, w[4-r:4+r+1]) for (sl, w) in c_init}
        s_db = {(sl, w[4-r:4+r+1]) for (sl, w) in c_db}
        s_eu = {(sl, w[4-r:4+r+1]) for (sl, w) in c_e_union}
        s_ec = {(sl, w[4-r:4+r+1]) for (sl, w) in (c_e_common or set())}
        diff_db_ec = sorted(s_ec - s_db)
        diff_all_ec = sorted(s_ec - (s_db | s_init))
        diff_all_eu = sorted(s_eu - (s_db | s_init))
        print(f"  r={r} ({2*r+1}-cell): E_common \\ D/B = {len(diff_db_ec)} | E_common \\ (init+D/B) = {len(diff_all_ec)} | E_union \\ (init+D/B) = {len(diff_all_eu)}")
        if r <= 2 and (diff_db_ec or diff_all_eu):
            for sl, w in diff_db_ec[:12]:
                in_init = (sl, w) in s_init
                print(f"    [E_common \\ D/B] slot={sl} win={''.join(map(str, w))} (in_init={in_init})")
            for sl, w in [x for x in diff_all_eu if x not in diff_db_ec][:8]:
                print(f"    [E_union \\ (init+D/B)] slot={sl} win={''.join(map(str, w))}")
