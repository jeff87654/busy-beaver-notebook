import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

# Let's verify how Rule D and Rule B_z act on B mod 8 (or mod 16)!
# Wait: in Rule B_z, d_{z-1} = (B - 1)//2 + 4 - z.
# Notice that to know (B - 1)//2 mod 2^m, we need B mod 2^{m+1}!
# Wait: how many times is B divided by 2 along the entire cascade?
# No! Look at the LAST time z=2 (i.e. d_2 = 1 -> 0) happens:
# At that moment, the state becomes:
#   (B = 1; d_0 = 1, d_1 = (B_prev - 1)//2 + 2, 0, 0, ..., 0)
# First, Rule D runs on (B = 1; d_0 = 1, d_1):
#   B becomes 1 + 6(1) = 7!
#   So just before d_1 is consumed, the state is:
#   (B = 7; 0, d_1, 0, 0, ..., 0)
# Then Rule B_1 + Rule D runs d_1 times on B = 7:
#   After d_1 steps of B -> 3B + 16 = 3(B + 8) - 8:
#   B_final = 3^{d_1} * (7 + 8) - 8 = 15 * 3^{d_1} - 8!
# WAIT A SECOND!
# Look at that formula:
#   B_final = 15 * 3^{d_1} - 8 !!
# Regardless of what d_2, d_3, ..., d_{k-1} were, as long as k >= 3 and the last z >= 2 step
# had z = 2 (which is ALWAYS true because d_2 is decremented to 0 one unit at a time, and each
# time d_2 > 0 is decremented with z=2, it sets d_1 = (B_prev - 1)//2 + 2 >= 2 > 0!),
# the VERY LAST z >= 2 step in ANY cascade with k >= 3 digits is a z = 2 step:
#   (B_prev; 0, 0, 1, 0, ..., 0) -> (1; 1, d_1, 0, ..., 0) -> (7; 0, d_1, 0, ..., 0)
#   -> B_final = 15 * 3^{d_1} - 8 !!

# WAIT A SECOND!
# Look at B_final = 15 * 3^{d_1} - 8 modulo 4:
# Since 15 == 3 (mod 4) and 8 == 0 (mod 4):
#   B_final == 3^{d_1 + 1} (mod 4)!
# So B_final mod 4 depends ONLY on the parity of d_1 = (B_prev - 1)//2 + 2,
# which depends ONLY on B_prev mod 4!
# Wait: what was B_prev?!
# If d_2 came from (7; 0, d_1', 1, 0, ...) via d_1' steps of B -> 3B + 16, then
# EVERY intermediate B before a z=2 step ALSO had the form:
#   B_prev = 15 * 3^{d_1'} - 8 (if preceded by z=2)
#   OR B_prev = 3^{d_1'} * (1 + 6 + 8) - 8 = 15 * 3^{d_1'} - 8 (since for ANY z >= 2,
#   Rule B_z sets B = 1 and d_0 = 1, so after Rule D, B = 7 before d_1 is consumed!!)!

# HOLD EVERYTHING!
# Let's check that!
# For ANY z >= 2:
# Rule B_z produces:
#   (B = 1; d_0 = 1, d_1 = 1, ..., d_{z-1} = (B_old - 1)//2 + 4 - z, ...)
# Because z >= 2, d_0 IS ALWAYS SET TO 1!
# Wait: what if z = 2? Then d_0 = 1, and d_1 = (B_old - 1)//2 + 2!
# What if z >= 3? Then d_0 = 1, d_1 = 1, ..., and before d_1 is exhausted, d_2 >= 1 will be
# decremented by a z = 2 step!
# Therefore, the LAST step with z >= 2 before exhaustion is ALWAYS z = 2!
# And EVERY step before a z >= 2 step (after the very first z >= 2 step) starts from
# B = 1, d_0 = 1 -> B = 7, followed by d_1 >= 1 steps of B -> 3B + 16!
# Therefore, after the first z >= 2 step, EVERY B at the moment z >= 2 is triggered satisfies:
#   B = 15 * 3^{d_1} - 8 !!
# Let's check what 15 * 3^{d_1} - 8 is modulo 8!
# Since 15 == -1 (mod 8) and 8 == 0 (mod 8):
#   B = 15 * 3^{d_1} - 8 == -3^{d_1} (mod 8)!
#Wait:
# - If d_1 is EVEN: 3^{d_1} == 1 (mod 8), so B == -1 == 7 (mod 8)!
#   Then in the NEXT z=2 step, the new d_1 is:
#   d_1_next = (B - 1)//2 + 2.
#   Since B == 7 (mod 8), (B - 1)//2 == 3 (mod 4), so d_1_next = 3 + 2 == 5 == 1 (mod 2) (ODD)!
# - If d_1 is ODD: 3^{d_1} == 3 (mod 8), so B == -3 == 5 (mod 8)!
#   Then in the NEXT z=2 step, what is (B - 1)//2 + 2?!
#   Since B == 5 (mod 8), (B - 1)//2 == 2 (mod 4), so d_1_next = 2 + 2 == 4 == 0 (mod 2) (EVEN)!

# Let's test this exact recurrence against actual cascade evaluation!
def eval_cascade_exact(B, ds):
    ds = list(ds)
    while any(d > 0 for d in ds):
        if ds[0] > 0:
            B += 6 * ds[0]
            ds[0] = 0
        else:
            z = 0
            while z < len(ds) and ds[z] == 0:
                z += 1
            ds[z] -= 1
            for i in range(z - 1):
                ds[i] = 1
            ds[z - 1] = (B - 1) // 2 + 4 - z
            B = 1
    return B

for B0 in (1, 3, 5):
    for d0 in (1, 2):
        for d1 in (1, 2, 3):
            for d2 in (1, 2, 3):
                ds = [d0, d1, d2]
                B_fin = eval_cascade_exact(B0, ds)
                print(f"B0={B0}, ds={ds} -> B_fin={B_fin}, B_fin mod 8 = {B_fin % 8}, B_fin mod 4 = {B_fin % 4}")
