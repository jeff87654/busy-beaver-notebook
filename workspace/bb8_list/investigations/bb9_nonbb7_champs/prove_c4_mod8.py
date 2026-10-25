import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

def eval_fast_small(B, ds):
    """Exact evaluation for small lists using fast d0, d1 jump."""
    ds = list(ds)
    while any(d > 0 for d in ds):
        if ds[0] > 0:
            B += 6 * ds[0]
            ds[0] = 0
        elif len(ds) > 1 and ds[1] > 0:
            B = (B + 8) * (3 ** ds[1]) - 8
            ds[1] = 0
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

# Verify on [1, 1, 1], [1, 1, 1, 1]
for k in (1, 2, 3):
    b_fin = eval_fast_small(5, [1]*k)
    print(f"k={k}: B_fin = {b_fin}, B_fin mod 8 = {b_fin % 8}")

# Now let's trace the mod-8 / parity tower for general z!
# Define T(z, b_mod8): the resulting B mod 8 after reducing (B; 0^z, 1) -> (B_out; 0^{z+1})
# No: let's define R(z, d): the resulting B mod 8 starting from (B_init(z); 0^z, d) down to (B_out; 0^{z+1}),
# where B_init(z) is the state reached after (1; 1, 1, ..., 1 (z copies)) finishes its first z digits!
# Wait: let's compute B_init(z) mod 8 for z = 1, 2, 3, ..., 25!
# Base cases:
# For (B=1; d_0=1): B_init(1) = 1 + 6 = 7 == 7 (mod 8).
# To reduce (B; 0, d_1) -> (B'; 0, 0):
#   B' = 3^{d_1} (B + 8) - 8 == 3^{d_1} * B (mod 8).
# For (B=1; 1, 1): B = 7, d_1 = 1 -> B_init(2) = 3^1 * 7 = 21 == 5 (mod 8).
# In general, for z >= 2:
# Suppose we are at (B; 0^z, d_z).
# One step of Rule B_z sets:
#   (1; 1, 1, ..., 1 (z-1 copies), d_{z-1} = (B - 1)//2 + 4 - z, d_z - 1)
# Then reducing the first (z-1) ones gives B_init(z-1) mod 8!
# And then reducing d_{z-1} at level (z-1) starting from B_init(z-1) gives the new B after 1 decrement of d_z!

def step_level(z, B_mod8, d):
    """Reduce (B; 0^z, d) -> B_out mod 8."""
    cur_B = B_mod8
    for _ in range(d):
        d_prev = ((cur_B - 1) // 2 + 4 - z) % 2 # Since period in d is 2!
        if d_prev == 0:
            d_prev = 2
        # After setting (1; 1^{z-1}, d_{z-1}), reducing (1; 1^{z-1}, d_prev) is reduce_ones(z, d_prev)
        cur_B = reduce_ones(z, d_prev)
    return cur_B

B_init = {1: 7}
def reduce_ones(z, d_top):
    """Reduce (1; 1^{z-1}, d_top) where d_top is at index z-1 (1-indexed level z)."""
    if z == 1:
        # (1; d_0) -> 1 + 6*d_0 mod 8
        return (1 + 6 * d_top) % 8
    if z == 2:
        # (1; 1, d_1) -> (7; 0, d_1) -> 7 * 3^{d_1} mod 8
        return (7 * pow(3, d_top, 8)) % 8
    # For z >= 3: first reduce (1; 1^{z-1}) to get B_init[z-1], then apply d_top steps at level z-1
    b = B_init[z - 1]
    return step_level(z - 1, b, d_top)

for z in range(2, 25):
    B_init[z] = reduce_ones(z, 1)
    # Also compute M = (B_init[z] - 2*z + 3) // 2 mod 2 when starting from (1; 1^z)!
    print(f"z={z:2d}: B_init(z) mod 8 = {B_init[z]}")

# Now let's compute B_fin mod 8 for (B=5; 1^k) for k = 1..25!
def eval_mod8_from_start(B0, ds):
    # We can reduce from left to right!
    # Start at level 0 with B = B0:
    b = (B0 + 6 * ds[0]) % 8
    if len(ds) == 1:
        return b
    b = (b * pow(3, ds[1], 8)) % 8
    for z in range(2, len(ds)):
        b = step_level(z, b, ds[z])
    return b

print("\n=== Exact B_fin mod 8 and M mod 2 for E[0] 1^5 (0011)^k 001 ===")
for k in range(1, 25):
    b8 = eval_mod8_from_start(5, [1]*k)
    # M = (B - 2k + 3) // 2, so M mod 2 = ((b8 - 2*k + 3) // 2) % 2
    m_par = ((b8 - 2*k + 3) // 2) % 2
    print(f"k={k:2d}: B_fin mod 8 = {b8}, M_1 mod 2 = {m_par} ({'ODD' if m_par else 'EVEN'})")
