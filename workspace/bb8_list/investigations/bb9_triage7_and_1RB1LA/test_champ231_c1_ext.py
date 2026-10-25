import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
T_STR = "L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1"

# Let's test all 14 7-state completions of C1 on K([0]*k; a; 0) for k=1,2,3 and a=k,k+1,k+2
print("=== Testing all 14 7-state completions of C1 on champ_231 at E(k, a) ===")
for bit in "01":
    for d in "LR":
        for st in "ABCDEFG":
            cand = bit + d + st
            tm = M1.replace("---", cand)
            T = kl.tmpl(tm, T_STR)
            res = []
            for k in (1, 2):
                for a in (k, k+1, k+2):
                    ev = kl.run(tm, [0]*k, a, 0, steps=200000, nchg=0, maxl=5000, T=T, pall=1)
                    # Find first K event after step 300 (when C1 is hit)
                    found = None
                    for e in ev[1:]:
                        if len(e) > 1 and e[1] > 300 and e[0] == 'K':
                            found = f"K(len={len(e[2])},ds={e[2][:4]}..;a={e[3]};b={e[4]})@{e[1]}"
                            break
                        elif e[0] == 'H':
                            found = f"H@{e[1]}"
                            break
                        elif e[0] in ('T', 'M', 'C'):
                            found = f"{e[0]}"
                            break
                    if not found:
                        found = f"last={ev[-1][:3]}"
                    res.append(f"({k},{a}):{found}")
            print(f"  C1={cand}: " + " | ".join(res))
