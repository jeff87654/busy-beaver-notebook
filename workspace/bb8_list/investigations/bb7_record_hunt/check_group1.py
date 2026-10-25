import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
import subprocess, os

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ.get('PATH', '')
RK7 = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\rank\rk7.exe'

g1 = [
    ("G1_1", "1RB1LA_1LC0RC_0LA0LD_0RE1LD_0RF1LB_---0RG_1RC1RG", "L,D,-,1,0,1,0,1,0,1110"),
    ("G1_2", "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG", "L,A,-,1,0,1,0,1,0,0"),
    ("G1_3", "1RB1LA_1RC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG", "L,A,-,1,0,1,0,1,0,0"),
    ("G1_4", "1RB1RA_0LC0LE_1RD1LC_1LB0RB_0RF1LE_0RG1LD_---0RA", "L,E,-,1,0,1,0,1,0,1110"),
    ("G1_5", "1RB1RA_0LC0LF_0RD1LC_1RA1RE_1LF1RG_1LB1LF_---0RA", "L,C,-,1,0,1,0,1,0,10"),
    ("G1_6", "1RB1RA_0LC0LF_1RD1LC_1LA1RE_1LB0RG_1LE1LF_---0RA", "L,F,-,1,0,1,0,1,0,-"),
    ("G1_7", "1RB1RA_0LC0LF_1RD1LC_1LG1RE_1LB0RG_1LE1LF_---0RA", "L,E,-,1,0,1,0,1,0,-"),
    ("G1_8", "1RB1RA_0LC0LF_1RD1LC_1RA1RE_1LB0RG_1LE1LF_---0RA", "L,F,-,1,0,1,0,1,0,-"),
    ("G1_9", "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1RA1LG_---0LE", "R,B,-,1,0,1,0,1,0,1"),
]

for name, m, t_str in g1:
    t_args = t_str.split(',')
    # Probe R3: [1,2] + [0]*k, a=0, b=15..18 for k=1..4
    cfgs = []
    for k in range(1, 5):
        for b in (15, 16, 17, 18):
            cfgs.append(([1, 2] + [0]*k, 0, b))
    inp = ''.join(f"{','.join(map(str, ds))} {a} {b}\n" for ds, a, b in cfgs)
    p = subprocess.run([RK7, 'probe', m] + t_args + ['500000'], input=inp, capture_output=True, text=True, creationflags=0x40)
    lines = p.stdout.strip().splitlines()
    print(f"=== {name}: {m} ({t_str}) ===")
    for (ds, a, b), res in zip(cfgs, lines):
        if b in (15, 16):
            print(f"  K({ds}; {a}; {b}) -> {res}")
