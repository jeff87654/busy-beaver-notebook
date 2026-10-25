import sys, os, random
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
from egrid import short

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
M2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"
T_STR = "L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1"

def next_k(tm, T, ds, a, b=0, steps=10000000):
    ev = kl.run(tm, ds, a, b, steps=steps, nchg=0, maxl=50000, T=T, pall=1)
    for e in ev[1:]:
        if e[0] == 'H':
            return ('HALT', e[1], e[2], e[3])
        if e[0] == 'K' and e[4] == 0:
            return ('K', e[1], e[2], e[3], e[4])
    return ('T', ev[:5])

T = kl.tmpl(M1, T_STR)
print("=== Probing D and Bk of champ_231 ===")
for d in (1, 2, 3):
    row = []
    for a in range(1, 7):
        r = next_k(M1, T, [2, d], a)
        row.append(f"a={a}->({short(r[2])};{r[3]})@{r[1]}" if r[0]=='K' else f"a={a}->{r}")
    print(f"  D [2, {d}; a; 0]: " + ", ".join(row))

for k in range(1, 7):
    row = []
    for a in range(1, 9):
        r = next_k(M1, T, [2] + [0]*k, a)
        row.append(f"a={a}->({short(r[2])};{r[3]})" if r[0]=='K' else f"a={a}->{r[0]}@{r[1]}")
    print(f"  B{k} [2, 0^{k}; a; 0]: " + ", ".join(row))

print("\n=== Probing Exhaustion E [0^k; a; 0] for k=1..20, a=k..k+4 ===")
for k in (1, 2, 5, 10, 15, 20):
    row = []
    for a in (0, k-1, k, k+1, k+2, k+5):
        if a < 0: continue
        r = next_k(M1, T, [0]*k, a)
        row.append(f"a={a}->{r[0]}@{r[1]}" if r[0]=='HALT' else (f"a={a}->({short(r[2])};{r[3]})" if r[0]=='K' else f"a={a}->T"))
    print(f"  E(k={k:2d}): " + ", ".join(row))

def pred_champ231(ds, a):
    if all(x == 0 for x in ds):
        k = len(ds)
        # Check when E(k, a) halts!
        return 'HALT'
    if ds[-1] > 0:
        return (ds[:-1] + [ds[-1] - 1], 3 * a + 3)
    k = 0
    while ds[-1 - k] == 0:
        k += 1
    y = ds[-1 - k]
    # Check refill formula from B_k output
    return (ds[:-1 - k] + [y - 1, 3 * a + 3 - k] + [1] * (k - 1), 1)

print("\n=== Random validation of pred_champ231 on 100 configs (with a >= k) ===")
random.seed(42)
for M in (M1, M2):
    ok = bad = to = 0
    for _ in range(100):
        n = random.randint(1, 5)
        ds = [random.randint(0, 3) for _ in range(n)]
        # Ensure if trailing zeros k, a >= k
        k = 0
        while k < len(ds) and ds[-1 - k] == 0:
            k += 1
        a = random.randint(max(1, k), max(6, k + 4))
        p = pred_champ231(ds, a)
        l_res = next_k(M, T, ds, a)
        l = 'HALT' if l_res[0] == 'HALT' else (l_res[2], l_res[3]) if l_res[0] == 'K' else 'T'
        if l == 'T': to += 1
        elif p == l: ok += 1
        else:
            bad += 1
            if bad <= 5: print("  MISMATCH:", M, ds, a, "pred:", p, "lit:", l_res)
    print(f"  {M}: ok={ok}, bad={bad}, timeout={to}")
