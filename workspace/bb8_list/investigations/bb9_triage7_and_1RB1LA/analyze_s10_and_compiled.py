import sys, os, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
from egrid import short

HERE = os.path.dirname(os.path.abspath(__file__))

# 1. Compile henum_1RB1LA_9.cpp
cpp_file = os.path.join(HERE, 'henum_1RB1LA_9.cpp')
exe_file = os.path.join(HERE, 'henum_1RB1LA_9.exe')
p = subprocess.run(['g++', '-O3', '-static', cpp_file, '-o', exe_file], capture_output=True, text=True)
print("Compile henum_1RB1LA_9:", p.returncode, p.stderr)

def next_k_s10(tm, T, B, ds, a, steps=5000000):
    ev = kl.run(tm, ds, a, B, steps=steps, nchg=0, maxl=50000, T=T, pall=1)
    for e in ev[1:]:
        if e[0] == 'H':
            return ('HALT', e[1], e[2], e[3])
        if e[0] == 'K' and e[4] == B:
            return ('K', e[1], e[2], e[3], e[4])
    return ('T', ev[:5])

def probe_s10(name, tm, t_str, B=0):
    T = kl.tmpl(tm, t_str)
    print(f"\n=== {name}: {tm} ({t_str}, B={B}) ===")
    print("  D probes [2, d; a; B]:")
    for d in (1, 2):
        row = []
        for a in range(0, 6):
            res = next_k_s10(tm, T, B, [2, d], a, steps=500000)
            row.append(f"a={a}->({short(res[2])};{res[3]})" if res[0]=='K' else f"a={a}->{res[0]}")
        print(f"    d={d}: " + ", ".join(row))
    print("  Bk probes [2, 0^k; a; B]:")
    for k in (1, 2, 3, 4):
        row = []
        for a in range(0, 7):
            res = next_k_s10(tm, T, B, [2] + [0]*k, a, steps=1000000)
            row.append(f"a={a}->({short(res[2])};{res[3]})" if res[0]=='K' else f"a={a}->{res[0]}")
        print(f"    k={k}: " + ", ".join(row))
    print("  Exhaustion E(k; a) = [0^k; a; B]:")
    for k in (0, 1, 2, 3, 4):
        row = []
        for a in range(0, 9):
            res = next_k_s10(tm, T, B, [0]*k, a, steps=2000000)
            row.append(f"a={a}->({short(res[2])};{res[3]})" if res[0]=='K' else f"a={a}->{res[0]}")
        print(f"    k={k}: " + ", ".join(row))

probe_s10("r4_1_rrrr", "1RB0RD_0LC1LC_1LE1LD_1RE1LB_1RG1LF_---0LE_1RA1RG", "L,C,P=-,u=1,s=10,d=1d+0,b=3b+0,S=-", B=0)
probe_s10("r4_2_rrFFr", "1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA0LE", "R,B,P=-,u=1,s=10,d=1d+0,b=3b+1,S=-", B=0)
probe_s10("r4_3_rrFFr", "1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA1RB", "R,B,P=-,u=1,s=10,d=1d+0,b=3b+1,S=-", B=0)
probe_s10("r4_4_rFrL", "1RB0RD_0RC1RG_1RD1RC_1LD0LE_0RB1LF_0LC1LE_---1RA", "L,E,P=-,u=1,s=10,d=1d+0,b=2b+1,S=10", B=2)
