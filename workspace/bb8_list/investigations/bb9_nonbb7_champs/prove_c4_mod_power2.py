import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

# Let's generalize prove_c4_mod8.py to mod 2^m!
# At level 1 (index z=1): B' = 3^{d_1} * (B + 8) - 8.
# Modulo 2^m, 3^{d_1} has period 2^{m-2} (for m >= 3).
# And at level z >= 2: d_{z-1} = (B - 1)//2 + 4 - z.
# Notice that to know d_{z-1} mod 2^{k}, we need B mod 2^{k+1}!
# Since at level 1 we need d_1 mod 2^{m-2} to get B' mod 2^m,
# at level 2 we only need B mod 2^{m-1} to get d_1 mod 2^{m-2}, which STILL gives B' mod 2^m!
# Wait: at level 1, B' = 15 * 3^{d_1} - 8!
# Because 3^{d_1} mod 2^m ONLY depends on d_1 mod 2^{m-2},
# to know B' mod 2^m after level 1, we ONLY need d_1 mod 2^{m-2}!
# And since d_1 = (B_prev - 1)//2 + 2, to know d_1 mod 2^{m-2}, we ONLY need B_prev mod 2^{m-1}!!
# WAIT A SECOND!
# Every step up the tower (z -> z+1) LOSES AT MOST 1 BIT OF PRECISION, No — it GAINS 1 bit of precision!
# Wait: if B_prev is known mod 2^{m-1}, then d_1 = (B_prev - 1)//2 + 2 is known mod 2^{m-2},
# and therefore 15 * 3^{d_1} - 8 is known mod 2^m!!
# Read that again!
#   B_prev mod 2^{m-1}  ===>  d_1 mod 2^{m-2}  ===>  B_next = 15 * 3^{d_1} - 8 mod 2^m !!
# That means the map B_prev -> B_next = 15 * 3^{(B_prev - 1)//2 + 2} - 8 is a CONTRACTION in the 2-adic metric!
# Every single application of z=2 DOUBLES the 2-adic precision (gains 1 bit mod 2^m)!!

# Let's verify this 2-adic contraction!
MOD = 1 << 20 # mod 2^20

def f_z2(B):
    """One z=2 step: (B; 0, 0, 1) -> (1; 1, d1, 0) -> (7; 0, d1, 0) -> 15 * 3^{d1} - 8 mod 2^20."""
    d1 = (B - 1) // 2 + 2
    return (15 * pow(3, d1, MOD) - 8) % MOD

# Let's check iterates of f_z2 starting from B = 37 (which is B_init(2)):
b = 37
for step in range(1, 15):
    b_next = f_z2(b)
    print(f"iter {step:2d}: b mod 64 = {b % 64:2d}, b mod 256 = {b % 256:3d}, M=(b-39)//2 mod 32 = {((b - 39)//2) % 32}")
    b = b_next
