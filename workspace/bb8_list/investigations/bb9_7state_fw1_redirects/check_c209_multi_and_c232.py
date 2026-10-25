import sys, os, subprocess, glob
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

print("=== 1. DEEP AUDIT OF 44-DIGIT MULTI? AND OTHER MULTI?/W1-LOOPER IN c209+ ===")
targets = [
    ("multi_44_1", "1RB1LC_1LA1LD_1LA---_0LA1LE_0RF0RG_1LB0RG_0LF1RE", "R,F,P=1,u=01,s=0,d=1d+0,b=1b+0,S=0"),
    ("multi_44_2", "1RB1LC_1LA1LD_1LA---_0LA1LE_0RF0RG_1LB1RD_0LF1RE", "R,F,P=1,u=01,s=0,d=1d+0,b=1b+0,S=0"),
    ("multi_E_1",  "1RB1LD_1RC1RD_1LB0RG_0RC1RE_0LA0LF_0RA1LE_0LA---", "L,E,P=1,u=01,s=0,d=1d+0,b=1b+0,S=-"),
    ("multi_E_2",  "1RB1LD_1RC1RD_1LB1RG_0RC1RE_0LA0LF_0RA1LE_1RC---", "L,E,P=1,u=01,s=0,d=1d+0,b=1b+0,S=-"),
    ("w1_G_1",     "1RB1LD_0RC1LB_0LD0RE_1LA0LF_0RG1RC_1LG---_0LA0LB", "R,G,P=100,u=10,s=0,d=1d+0,b=1b+0,S=0"),
    ("w1_E_1",     "1RB1LD_0RC1LB_0LD0RE_1LA1LF_1RB1RC_1LG---_0LA0LB", "R,E,P=100,u=10,s=0,d=1d+0,b=1b+0,S=-"),
    ("champ_1",    "1RB1LD_1RC0RF_1LA---_0RE0LD_1LC0RE_0LA1RG_0LA1RA", "L,D,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
    ("champ_3",    "1RB1LD_1RC0RF_1LA---_0RE0LD_1LC0RE_1LF1RG_0LA1RA", "L,D,P=10,u=1,s=0,d=1d+0,b=1b+0,S=-"),
]

for name, tm, t_str in targets:
    T = kl.tmpl(tm, t_str)
    b_res = kl.blank(tm, steps=100000, maxl=30, T=T)
    k_lines = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" for e in b_res if e[0] == 'K']
    print(f"\n[{name}] {tm} ({t_str})")
    print(f"  blank K-lines ({len(k_lines)}): {' -> '.join(k_lines[:10])}")
    # Test D, B1, B2, and boundary contraction [0, 1], [0, 0, 1], [2, 0, 0], [];a
    for label, ds, a, B in [
        ("D [2,2;3]", [2,2], 3, 1),
        ("B1 [2,0;3]", [2,0], 3, 1),
        ("B2 [2,0,0;3]", [2,0,0], 3, 1),
        ("lead0 [0,2;3]", [0,2], 3, 1),
        ("lead00 [0,0,2;3]", [0,0,2], 3, 1),
        ("top [1,0,0;4]", [1,0,0], 4, 1),
        ("top [2,0,0;4]", [2,0,0], 4, 1),
        ("E(;3;1)", [], 3, 1),
        ("E(;4;1)", [], 4, 1),
        ("E(;5;1)", [], 5, 1),
    ]:
        evs = kl.run(tm, ds, a, B, steps=50000, nchg=0, maxl=15, T=T, pall=1)
        nxt = next((e for e in evs[1:] if e[0] == 'H' or (e[0] == 'K' and e[2] != ds)), evs[-1] if evs else None)
        if nxt and nxt[0] == 'K':
            print(f"  {label:18s} -> K({short(nxt[2])};{nxt[3]};{nxt[4]})@{nxt[1]}")
        else:
            print(f"  {label:18s} -> {nxt}")

print("\n=== 2. CHECKING NEW FILES c00232+ ===")
dl2_dir = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl2_out'
new_files = sorted(glob.glob(os.path.join(dl2_dir, 'c*.tsv')))
new_files = [f for f in new_files if int(os.path.basename(f)[1:6]) >= 232]
tms = []
for f in new_files:
    with open(f) as fp:
        for line in fp:
            if line.startswith('1RB') and '\t' in line:
                tms.append(line.split('\t')[0])
print(f"Found {len(tms)} machines in {len(new_files)} files (c00232+): {tms}")
