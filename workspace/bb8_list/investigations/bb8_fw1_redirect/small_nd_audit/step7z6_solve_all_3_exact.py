import os, sys

# Let's trace G#23 from [1, 1, 233298]; 3!
# Wait: in G#23, how many steps does it take to reduce [1, 1, 233298]; 3?
# At each step on [..., d]; a in G#23:
#   d decreases by k >= 1, and a multiplies by ~(3/2)^k!
# Wait: if d = 233298, then a grows to ~(3/2)^233298 (a 41,000-digit integer)!
# Can Python do 233,298 steps on a 41,000-digit integer?
# Wait: why did we compute full bigints in step7z3 when k and xs only depend on the LOWEST ~30 bits of a?!
# HOLD EVERYTHING!!
# Look at d_step_G23(a) and d_step_G24(a):
#   Does k (the number of decrements of d) depend on the full integer a, or ONLY on the 2-adic valuation of a + const?!
#   LET'S CHECK!!

# In d_step_G23(a):
#   - a odd: k = 1, a' = (3*a + 3) // 2
#   - a = 4j: k = 2, a' = (9*a + 16) // 4
#   - a = 4j + 2:
#     m = a // 2 (odd)
#     x_1 = (3*m + 3) // 2 = (3*a + 6) // 4
#     while x_i is odd: x_{i+1} = (3*x_i + 1) // 2
#     Notice: x_{i+1} + 1 = (3*(x_i + 1)) // 2!
#     SO x_i + 1 = (3/2)^{i-1} * (x_1 + 1)!!
#     And x_1 + 1 = (3*a + 10) // 4!!
#     Therefore, the number of odd steps after x_1 is literally v_2(x_1 + 1) = v_2(3*a + 10) - 2!!
#     AND WHAT IS 3*a + 10 = 3*(a + 6) - 8?!
#     Wait: 3*a + 10 is divisible by 2^r if and only if:
#     k = v_2(3*a + 10) + 1 (for k >= 3)!!
#     Let's check that formula for G#23!!
#     - If a is odd: 3*a + 10 is odd -> v_2(3*a + 10) = 0 -> k = 1!
#     - If a == 0 (mod 4): 3*a + 10 == 2 (mod 4) -> v_2(3*a + 10) = 1 -> k = 2!
#     - If a == 6 (mod 8): 3*6 + 10 = 28 = 4 * 7 -> v_2(3*a + 10) = 2 -> k = 3!
#     - If a == 10 (mod 16): 3*10 + 10 = 40 = 8 * 5 -> v_2(3*a + 10) = 3 -> k = 4!
#     - If a == 2 (mod 32): 3*2 + 10 = 16 = 16 * 1 -> v_2(3*a + 10) = 4 -> k = 5!
#     - If a == 18 (mod 64): 3*18 + 10 = 64 = 64 * 1 -> v_2(3*a + 10) = 6 -> k = 7!

# MIND BLOWN!! Look at 3*a + 10 in G#23:
#   For ALL a >= 1 in G#23:
#     k = v_2(3*a + 10) + 1 !!
#   And what is a_next in terms of k = v_2(3*a + 10) + 1?!
#   - For k = 1: a' = (3*a + 3) // 2
#   - For k = 2: a' = (9*a + 16) // 4
#   - For k >= 3:
#     x_1 + 1 = (3*a + 10) // 4
#     x_{k-2} + 1 = 3^{k-3} * (3*a + 10) // 2^{k-1}
#     a' = (9 * x_{k-2} + 2) // 2 = (3^{k} * a + 10 * 3^{k-1} - 7 * 2^{k-1}) // 2^k !!

# Now check G#24!! What is the linear form in G#24?!
# In d_step_G24(a):
#   - a even: k = 1, a' = (3*a + 4) // 2
#   - a = 4j + 1: k = 2, a' = (9*a + 19) // 4
#   - a = 4j + 3:
#     m = (a - 1) // 2 (odd)
#     x_1 = (3*m + 5) // 2 = (3*a + 7) // 4
#     while x_i is odd: x_{i+1} = (3*x_i + 1) // 2 -> x_{i+1} + 1 = (3/2) * (x_i + 1)!
#     And x_1 + 1 = (3*a + 11) // 4 !!
#     So for ALL a >= 1 in G#24:
#       k = v_2(3*a + 11) + 1 !!
#     Check that!
#     - a even: 3*a + 11 is odd -> v_2 = 0 -> k = 1!
#     - a == 1 (mod 4): 3*a + 11 == 14 == 2 (mod 4) -> v_2 = 1 -> k = 2!
#     - a == 3 (mod 8): 3*3 + 11 = 20 = 4 * 5 -> v_2 = 2 -> k = 3!
#     - a == 15 (mod 16): 3*15 + 11 = 56 = 8 * 7 -> v_2 = 3 -> k = 4!
#     - a == 23 (mod 32): 3*23 + 11 = 80 = 16 * 5 -> v_2 = 4 -> k = 5!
#     - a == 7 (mod 64): 3*7 + 11 = 32 = 32 * 1 -> v_2 = 5 -> k = 6!

print("Verifying k = v_2(3*a + 10) + 1 for G#23 and k = v_2(3*a + 11) + 1 for G#24...")
for a in range(1, 100):
    v23 = (3*a + 10) & -(3*a + 10)
    k23 = v23.bit_length()
    if k23 == 1:
        an23 = (3*a + 3) // 2
    elif k23 == 2:
        an23 = (9*a + 16) // 4
    else:
        an23 = (3**k23 * a + 10 * 3**(k23-1) - 7 * 2**(k23-1)) // (2**k23)
    # Compare with d_step_G23
    from step7z3_simulate_23_24_27 import d_step_G23, d_step_G24
    k23_ref, an23_ref, _ = d_step_G23(a)
    assert (k23, an23) == (k23_ref, an23_ref), f"G23 mismatch at {a}: {(k23, an23)} vs {(k23_ref, an23_ref)}"

    v24 = (3*a + 11) & -(3*a + 11)
    k24 = v24.bit_length()
    if k24 == 1:
        an24 = (3*a + 4) // 2
    elif k24 == 2:
        an24 = (9*a + 19) // 4
    else:
        an24 = (3**k24 * a + 11 * 3**(k24-1) - 7 * 2**(k24-1)) // (2**k24)
    k24_ref, an24_ref, _ = d_step_G24(a)
    assert (k24, an24) == (k24_ref, an24_ref), f"G24 mismatch at {a}: {(k24, an24)} vs {(k24_ref, an24_ref)}"
print("100% EXACT MATCH for all a=1..100 on both G#23 and G#24!")
