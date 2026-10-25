import sys, os, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
from egrid import short

def strip0(ds):
    i = 0
    while i < len(ds) and ds[i] == 0:
        i += 1
    return ds[i:]

def next_k(tm, T, B, ds, A, steps=5000000):
    ev = kl.run(tm, ds, A, B, steps=steps, nchg=0, maxl=50000, T=T, pall=1)
    for e in ev[1:]:
        if e[0] == 'H':
            return ('HALT', e[1], e[2], e[3])
        if e[0] == 'K' and e[4] == B:
            return ('K', e[1], strip0(e[2]), e[3], e[4])
    return ('T', ev[:5])

def test_v_family(name, tm, side, q, B, S_str='-'):
    t_str = f"{side},{q},P=-,u=1,s=0,d=1d+0,b=1b+0,S={S_str}"
    T = kl.tmpl(tm, t_str)
    print(f"\n=== {name}: {tm} (v-coding {t_str}, B={B}) ===")
    ev = kl.blank(tm, 20000000, maxl=40, T=T)
    print("  Blank trace (filtered to b == B or H):")
    for e in ev:
        if e[0] == 'H' or (e[0] == 'K' and e[4] == B):
            print(f"    step {e[1]}: K({short(strip0(e[2]))}; A={e[3]}; B={e[4]})")
    print("  D probes [3, v; A; B]:")
    for v in (1, 2, 3):
        row = []
        for A in range(1, 7):
            res = next_k(tm, T, B, [3, v], A, steps=500000)
            if res[0] == 'K':
                row.append(f"A={A}->({short(res[2])};{res[3]})")
            else:
                row.append(f"A={A}->{res[0]}")
        print(f"    v={v}: " + ", ".join(row))
    print("  Bk probes [3, 0^k; A; B]:")
    for k in (1, 2, 3):
        row = []
        for A in range(1, 8):
            res = next_k(tm, T, B, [3] + [0]*k, A, steps=1000000)
            if res[0] == 'K':
                row.append(f"A={A}->({short(res[2])};{res[3]})")
            else:
                row.append(f"A={A}->{res[0]}")
        print(f"    k={k}: " + ", ".join(row))
    print("  Exhaustion E [; A; B] (for A=1..12):")
    for A in range(1, 13):
        res = next_k(tm, T, B, [], A, steps=2000000)
        if res[0] == 'K':
            print(f"    E(A={A:2d}) -> K({short(res[2])}; A'={res[3]}; B'={res[4]}) (len={len(res[2])}, step={res[1]})")
        else:
            print(f"    E(A={A:2d}) -> {res}")

# 1. r4_1_rrrr: L,C,P=-,u=1,s=10,d=1d+0,b=3b+0,S=- -> in v-coding (u=1,s=0,d=1d+0), B=0!
test_v_family("r4_1_rrrr", "1RB0RD_0LC1LC_1LE1LD_1RE1LB_1RG1LF_---0LE_1RA1RG", "L", "C", B=0)

# 2. r4_2_rrFFr and r4_3_rrFFr: R,B,P=-,u=1,s=10,d=1d+0,b=3b+1,S=- -> in v-coding, B=1!
test_v_family("r4_2_rrFFr", "1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA0LE", "R", "B", B=1)
test_v_family("r4_3_rrFFr", "1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA1RB", "R", "B", B=1)

# 3. r4_4_rFrL: L,E,P=-,u=1,s=10,d=1d+0,b=2b+1,S=10 -> in v-coding, B=5, S=10!
test_v_family("r4_4_rFrL", "1RB0RD_0RC1RG_1RD1RC_1LD0LE_0RB1LF_0LC1LE_---1RA", "L", "E", B=5, S_str='10')
