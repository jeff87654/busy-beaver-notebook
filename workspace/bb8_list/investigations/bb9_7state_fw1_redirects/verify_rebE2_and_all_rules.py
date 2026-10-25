import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

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

def trace_k_single(tm, t_str, B0, ds, a, maxs=500000, target_slot="A0"):
    t = kl.tmpl(tm, t_str)
    evs = kl.run(tm, ds, a, B0, steps=maxs, nchg=0, maxl=200, T=t, pall=1)
    ev1 = ('END',)
    stop_step = maxs
    for e in evs[1:]:
        if e[0] == 'H' or (e[0] == 'K' and e[4] == B0 and e[2] != ds):
            ev1 = e
            stop_step = e[1]
            break
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
    used = set()
    hits = []
    for step in range(1, stop_step + 1):
        c = tape.get(pos, 0)
        slot = chr(65 + q) + str(c)
        used.add(slot)
        if slot == target_slot:
            hits.append((step, format_full_tape(tape, pos, q)))
        if (q, c) not in tr:
            break
        W_bit, d, nq = tr[(q, c)]
        if W_bit: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d
        q = nq
    return ev1, sorted(used), hits

tm_rebE2 = "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC"
t_rebE2 = "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"

print("=== Testing reb_E2 on inner 1-digit borrows [5, 2, 1, 0^k; a] ===")
for ds in [[5, 2, 1], [5, 2, 1, 0], [5, 2, 1, 0, 0], [5, 0, 1, 0]]:
    for a in [3, 5]:
        ev, used, hits = trace_k_single(tm_rebE2, t_rebE2, 1, ds, a)
        print(f"  K({short(ds):10s}; a={a}; 1) -> {ev} | A0 hits={len(hits)} | used={used}")

print("\n=== Testing reb_E2 on [3, 0^k; a] and [1, 0^k; a] for a=7, 9 ===")
for ds in [[3, 0, 0], [1, 0, 0], [1, 0, 0, 0, 0, 0]]:
    for a in [7, 9]:
        ev, used, hits = trace_k_single(tm_rebE2, t_rebE2, 1, ds, a)
        print(f"  K({short(ds):10s}; a={a}; 1) -> {ev} | A0 hits={len(hits)}")
        for st, ft in hits:
            print(f"      step {st}: {ft}")

print("\n=== Testing multi_1 and w1loop_1 exhaustion with maxl=200 ===")
tm_m1 = "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF"
t_m1 = "R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1"
for ds in [[0, 0], [0], []]:
    for a in [1, 4]:
        ev, used, _ = trace_k_single(tm_m1, t_m1, 1, ds, a, maxs=500000)
        print(f"  multi_1 K({short(ds):6s}; a={a}; 1) -> {ev} | used={used}")

tm_w1 = "1RB0RE_1RC1RA_0LD0LE_1RE0LE_0RF1LC_1LC1RG_0RB---"
t_w1 = "L,F,P=1,u=10,s=0,d=2d+0,b=2b+1,S=-"
for ds in [[0, 0], [0], []]:
    for a in [1, 4]:
        ev, used, _ = trace_k_single(tm_w1, t_w1, 1, ds, a, maxs=500000)
        print(f"  w1loop_1 K({short(ds):6s}; a={a}; 1) -> {ev} | used={used}")
