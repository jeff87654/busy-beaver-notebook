import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

def parse_tm(tm_str):
    trans = {}
    for s_idx, block in enumerate(tm_str.split('_')):
        for b in (0, 1):
            cell = block[3*b:3*b+3]
            if cell == '---':
                trans[(s_idx, b)] = None
            else:
                w = int(cell[0])
                d = -1 if cell[1] == 'L' else 1
                ns = ord(cell[2]) - ord('A')
                trans[(s_idx, b)] = (w, d, ns)
    return trans

for name, tm in [
    ("multi_E_1", "1RB1LD_1RC1RD_1LB0RG_0RC1RE_0LA0LF_0RA1LE_0LA---"),
    ("multi_E_2", "1RB1LD_1RC1RD_1LB1RG_0RC1RE_0LA0LF_0RA1LE_1RC---"),
]:
    trans = parse_tm(tm)
    tape = {}
    head = 0
    state = 0
    print(f"=== {name} E0 visits during blank steps 1..200 ===")
    for step in range(1, 200):
        b = tape.get(head, 0)
        if state == 4 and b == 0 and tape.get(head-1, 0) == 0:
            mn = min(tape.keys())
            mx = max(tape.keys())
            s = ''.join(f"[{chr(ord('A')+state)}{tape.get(i,0)}]" if i == head else str(tape.get(i,0)) for i in range(mn-1, mx+2))
            print(f"  step {step:3d}: {s}")
        w, d, ns = trans[(state, b)]
        tape[head] = w
        head += d
        state = ns

print("\n=== Checking c00232+ MULTI? and W1-LOOPER ===")
for name, tm, t_str in [
    ("multi_c232", "1RB1LE_0LC1RE_1LB1RD_1RC---_0RC1RF_0LA0LG_0RA1LF", "L,F,P=1,u=01,s=0,d=1d+0,b=1b+0,S=-"),
    ("w1_c233",    "1RB1LE_0RC0RD_1LD0RD_0LA1RB_0LF---_1LB1LG_1LF0LD", "R,A,P=1,u=10,s=0,d=2d+0,b=2b+1,S=-"),
]:
    T = kl.tmpl(tm, t_str)
    b_res = kl.blank(tm, steps=100000, maxl=25, T=T)
    k_lines = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" for e in b_res if e[0] == 'K']
    print(f"\n[{name}] {tm} ({t_str})")
    print(f"  blank: {' -> '.join(k_lines[:10])}")
    for ds, a in [([2, 2], 3), ([2, 0], 3), ([2, 0, 0], 3), ([0, 0], 4), ([0], 4), ([], 4)]:
        evs = kl.run(tm, ds, a, 1, steps=50000, nchg=0, maxl=20, T=T, pall=1)
        nxt = next((e for e in evs[1:] if e[0] == 'H' or (e[0] == 'K' and e[4] == 1 and e[2] != ds)), evs[-1] if evs else None)
        print(f"  K({short(ds)};{a};1) -> {f'K({short(nxt[2])};{nxt[3]};{nxt[4]})@{nxt[1]}' if nxt and nxt[0]=='K' else nxt}")
