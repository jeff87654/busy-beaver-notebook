import os, sys
os.environ["PATH"] = r"C:\msys64\ucrt64\bin;" + os.environ.get("PATH", "")
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl

NEW_MULTI = "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF"
T_nm = kl.tmpl(NEW_MULTI, "R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1")

for k in range(0, 6):
    halts = []
    rebuilds = []
    for b in range(0, 15):
        ev = kl.run(NEW_MULTI, [0]*k, 0, b, steps=50000, nchg=2, maxl=10, T=T_nm, pall=0)
        if any(e[0] == 'H' for e in ev):
            halts.append(b)
        elif len(ev) > 1 and ev[1][0] == 'K':
            rebuilds.append((b, len(ev[1][2])))
    print(f"k={k}: HALTS at b={halts} | REBUILDS (b, len): {rebuilds[:5]}")
