import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

# Check reb_E1 with P=10, u=1, s=0, d=1d+0, b=1b+0, S=0, B=1!
# Wait: earlier with P=-, K(1, 2^7, 3; 3; 1) had a leading '1' (which is 10, i.e., P=10!).
# So with P=10, the leading '1' (10) IS the prefix P=10, and the digits are (2^7, 3; 3; 1) where digit '1' (10) is ZERO (d=0 in d=1d+1)!
# Let's check with P=10, u=1, s=0, d=1d+1, b=1b+0, S=0, B=1!

t_str = 'L,D,P=10,u=1,s=0,d=1d+1,b=1b+0,S=0'
base_tm = '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RA0RG_---0RB'
t = kl.tmpl(base_tm, t_str)

print("=== Blank trace of reb_E1 with P=10, d=1d+1 ===")
evs = kl.blank(base_tm, 20000, maxl=40, T=t)
for e in evs[:15]:
    if e[0] == 'K' and e[4] == 1:
        print(f"  step {e[1]:6d}: K({short(e[2])}; a={e[3]}; b={e[4]})")

def run_and_slots(tm, ds, a, B0=1, maxs=300000):
    evs = kl.run(tm, ds, a, B0, steps=maxs, nchg=0, maxl=50000, T=t, pall=1)
    ev1 = ('END',)
    stop_step = 5000
    for e in evs[1:]:
        if e[0] == 'H' or (e[0] == 'K' and e[4] == B0 and (e[2] != ds or e[3] != a)):
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
            used.add(chr(65+q) + str(c))
            break
        used.add(chr(65+q) + str(c))
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return ev1, sorted(used)

print("\n=== D, B1, B2, E on reb_E1 (P=10, d=1d+1) ===")
for label, ds, a in [
    ('D [2; 4]', [2], 4),
    ('B1 [2, 0; 4]', [2, 0], 4),
    ('B2 [2, 0, 0; 4]', [2, 0, 0], 4),
    ('E [0, 0; 4]', [0, 0], 4),
    ('E [0, 0; 5]', [0, 0], 5),
]:
    ev1, used = run_and_slots(base_tm, ds, a)
    print(f"  {label:16s} -> {ev1} | F0={'F0' in used} G0={'G0' in used} | used={used}")

print("\n=== Exhaustion E([0, 0]; a) across all 9 reb_E1 variants in hits_triage7.tsv ===")
F0_LIST = ['1RA', '0RC', '1RC', '0RD', '1RD', '0RE', '0RF', '1RF', '0RG']
for f0 in F0_LIST:
    tm = f"1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_{f0}0RG_---0RB"
    row = []
    for a in range(1, 8):
        ev1, used = run_and_slots(tm, [0, 0], a)
        if ev1[0] == 'K':
            row.append(f"a={a}:({short(ev1[2])};{ev1[3]})")
        elif ev1[0] == 'H':
            row.append(f"a={a}:H({ev1[2]}{ev1[3]}@{ev1[1]})")
        else:
            row.append(f"a={a}:{ev1[0]}")
    print(f"  F0={f0}: " + " | ".join(row))
