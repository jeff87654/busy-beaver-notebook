import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
import idle
import fit7

m = "1RB0LE_0RC1LF_1LD0RD_0LA---_1LA1RG_1RB1RF_0RH0LG_1RE1LD"
tmpl = "L,A,P=-,u=10,s=0,d=3d+2,b=1b+0,S=010101"

P = fit7.Prober(m, tmpl)
ks, end = P.trace(50000000, 200)
print(f"nK = {len(ks)}, end = {end}")
for i, k in enumerate(ks[:60]):
    print(f"{i:3d}: step={k[0]:10d} ds={k[1]} a={k[2]} b={k[3]}")
if len(ks) > 60:
    print("...")
    for i in range(len(ks)-20, len(ks)):
        k = ks[i]
        print(f"{i:3d}: step={k[0]:10d} ds={k[1]} a={k[2]} b={k[3]}")
