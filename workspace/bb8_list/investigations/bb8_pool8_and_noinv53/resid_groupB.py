import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

import numpy as np

M = 3 * (1 << 15)  # 98304, divisible by 3 and 2^15

# State is encoded as s = 2 * (U % M) + r, in 0 .. 2*M - 1
N = 2 * M

# Build Phi_0 on 0 .. N-1
Phi = []
s_arr = np.arange(N, dtype=np.int64)
U_arr = s_arr >> 1
r_arr = s_arr & 1
r_next = (U_arr + 1) & 1
U_next = (2 * U_arr + 8 - r_arr - r_next) % M
Phi0 = (U_next << 1) | r_next
Phi.append(Phi0)

def follow_orbit(f, s0):
    seen = {}
    orb = []
    x = int(s0)
    while x not in seen:
        seen[x] = len(orb)
        orb.append(x)
        x = int(f[x])
    t = seen[x]
    p = len(orb) - t
    return np.array(orb, dtype=np.int64), t, p

# Level 1: Phi_1(U, r) = Phi_0^U(9 - r, 0)
# Note: U >= 5 in real runs; for U >= t, index in orb is t + (U - t) % p
Phi1 = np.zeros(N, dtype=np.int64)
for r in (0, 1):
    s0 = ((9 - r) % M) << 1 | 0
    orb, t, p = follow_orbit(Phi0, s0)
    assert M % p == 0, f"Level 1 r={r}: period {p} does not divide M={M}"
    print(f"Level 1 r={r}: tail={t}, period={p}")
    # For U in 0..M-1, represent large Uequiv U mod M (so U_true >= t):
    idx = t + ((np.arange(M, dtype=np.int64) - t) % p)
    Phi1[(np.arange(M) << 1) | r] = orb[idx]
Phi.append(Phi1)

# Helper to apply tail [3, 2^{k-2}] to (6 - r, 1)
def get_ck(k, r):
    x = (((6 - r) % M) << 1) | 1
    for j in range(k - 2):
        f = Phi[j]
        x = int(f[int(f[x])])
    f = Phi[k - 2]
    x = int(f[int(f[int(f[x])])])
    return x

J = 100
bad = []
for k in range(2, J + 1):
    Phik = np.zeros(N, dtype=np.int64)
    f_prev = Phi[k - 1]
    for r in (0, 1):
        s0 = get_ck(k, r)
        orb, t, p = follow_orbit(f_prev, s0)
        if M % p != 0:
            bad.append((k, r, p))
        cnt = np.arange(M, dtype=np.int64) + 2 - 2 * k
        idx = t + ((cnt - t) % p)
        Phik[(np.arange(M) << 1) | r] = orb[idx]
    Phi.append(Phik)
    if k <= 12:
        print(f"Level {k}: period={p}, tail={t}")

print("Bad periods up to J=100:", bad)

# Verify against literal Blank trace of #17!
# At st=11379: K([3, 2^44]; a=3; b=0) -> r = 1, U = 2*3 + 0 - 1 = 5
def eval_list(ds, a, b):
    r = a & 1
    U = (2 * a + b - r) % M
    x = (U << 1) | r
    n = len(ds)
    for i in range(n - 1, -1, -1):
        lev = n - 1 - i
        f = Phi[min(lev, J)]
        for _ in range(ds[i]):
            x = int(f[x])
    U_out = x >> 1
    r_out = x & 1
    return U_out, r_out

# Check intermediate steps from blank trace:
# Start: [3, 2^44], a=3, b=0. Wait: to go from [3, 2^44], a=3, b=0 to [3, 2^42, 1, 35], a=1056, b=2:
# That reduced the suffix [2, 2] -> [1, 35], i.e. 1 step of Phi_1 (2->1) leaves [3, 2^42, 1, 0]?
# Wait: let's check K([3], 4, 0) -> K([], 56, 2) and K([4], 4, 1) -> K([], 128, 2) from earlier!
for ds, a, b in [([3], 4, 0), ([4], 4, 0), ([1], 4, 1), ([2], 4, 1), ([3], 4, 1), ([4], 4, 1), ([3, 2, 1], 8, 1)]:
    Uo, ro = eval_list(ds, a, b)
    # Reconstruct (a_final, b_final) mod M:
    # Actually at each R2 step, b_final = 2 - r_prev, wait: from (Uo, ro), since Uo = 2*a + b - ro and b in {1, 2}:
    # Wait: if ro == 0 (a even), Uo = 2*a + b, so b = 2 if Uo is even else 1!
    # If ro == 1 (a odd), Uo = 2*a + b - 1, so b = 1 if Uo is even else 2!
    b_out = 2 if ((Uo + ro) % 2 == 0) else 1
    a_out = ((Uo + ro - b_out) // 2) % (M // 2)
    status = "REBUILD" if (a_out + b_out) % 2 == 0 else "HALT"
    print(f"eval({ds}, a={a}, b={b}) -> U={Uo}, r={ro} => a={a_out}, b={b_out} ({status})")

# Now evaluate the blank-tape round 2 configuration of #17: K([3] + [2]*44, a=3, b=0)!
Uo, ro = eval_list([3] + [2]*44, 3, 0)
b_out = 2 if ((Uo + ro) % 2 == 0) else 1
a_out = ((Uo + ro - b_out) // 2) % (M // 2)
status = "REBUILD" if (a_out + b_out) % 2 == 0 else "HALT"
print(f"\nBLANK ROUND 2: eval([3, 2^44], a=3, b=0) -> U={Uo}, r={ro} => a={a_out}, b={b_out} ({status})")
