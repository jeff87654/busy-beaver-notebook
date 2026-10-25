import sys, os, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
from egrid import short

def probe_grid(name, tm, t_str, B, k_list=(0, 1, 2, 3, 4), a_list=range(0, 10), steps=2000000):
    T = kl.tmpl(tm, t_str)
    print(f"\n=== {name}: {tm} ({t_str}, B={B}) ===")
    for k in k_list:
        row = []
        for a in a_list:
            ev = kl.run(tm, [0]*k, a, B, steps=steps, nchg=0, maxl=20000, T=T, pall=1)
            res = 'T'
            for e in ev[1:]:
                if e[0] == 'H':
                    res = f"H@{e[1]}"
                    break
                if e[0] == 'K' and e[4] == B and e[2] != [0]*k:
                    res = f"({short(e[2])};{e[3]})"
                    break
            row.append(f"a={a}:{res}")
        print(f"  k={k}: " + " ".join(row))

# 1. champ_231: L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1 (and P=1 inclusive!)
probe_grid("champ_231 (P=100)", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB", "L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1", B=0, k_list=(0,1,2,3,4,5), a_list=range(0, 10))
probe_grid("champ_231 (P=-)", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB", "L,E,P=-,u=11,s=00,d=1d+0,b=1b+0,S=1", B=0, k_list=(0,1,2,3), a_list=range(1, 8))

# 2. multi_1: R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1
probe_grid("multi_1 (P=1)", "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF", "R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1", B=1, k_list=(0,1,2,3,4), a_list=range(1, 10))

# 3. reb_E1: L,D,P=10,u=1,s=0,d=2d+0,b=2b+1,S=0 -> in u=1,s=0,d=1d+0,b=1b+0, B=1
probe_grid("reb_E1 (P=-,d=1d+0)", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RA0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", B=1, k_list=(0,1,2), a_list=range(1, 10))

# 4. reb_E2: L,F,P=-,u=1,s=0,d=2d+0,b=2b+1,S=0 -> in d=1d+0, B=1
probe_grid("reb_E2 (P=-,d=1d+0)", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC", "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", B=1, k_list=(0,1,2), a_list=range(1, 10))

# 5. reb_A2: R,D,P=101,u=001,s=0,d=1d+0,b=2b+1,S=-
probe_grid("reb_A2 (P=101)", "1RB0RC_1LA0RC_0LG1RD_1LE0LB_1LG1LF_1LD---_0RA0LC", "R,D,P=101,u=001,s=0,d=1d+0,b=2b+1,S=-", B=1, k_list=(0,1,2,3), a_list=range(1, 10))

# 6. reb_B2: R,A,P=10,u=01,s=10,d=1d+0,b=1b+0,S=0
probe_grid("reb_B2 (P=10)", "1RB0LE_1LC1LG_0LD1LB_1RE0RB_0RF1RF_0LA0RE_0LC---", "R,A,P=10,u=01,s=10,d=1d+0,b=1b+0,S=0", B=2, k_list=(0,1,2,3), a_list=range(1, 10))

# 7. reb_C1: L,E,P=10,u=100,s=0,d=1d+0,b=1b+0,S=1
probe_grid("reb_C1 (P=10)", "1RB0LC_1LA0LC_0RD1LE_0LB0RC_1RF0RA_1RD1RG_1RE---", "L,E,P=10,u=100,s=0,d=1d+0,b=1b+0,S=1", B=2, k_list=(0,1,2,3), a_list=range(1, 10))

# 8. reb_D1: L,E,P=1001,u=010,s=00,d=1d+0,b=1b+0,S=-
probe_grid("reb_D1 (P=1001)", "1RB0RD_1RC---_0RD1RA_0RE0RA_0LF0LE_1LG0RE_0LA1LF", "L,E,P=1001,u=010,s=00,d=1d+0,b=1b+0,S=-", B=1, k_list=(0,1,2,3), a_list=range(1, 10))
