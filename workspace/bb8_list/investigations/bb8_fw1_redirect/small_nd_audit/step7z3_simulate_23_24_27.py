import os, sys

# 1. Verify exact step function for G#23 and G#24 and trace their blank trajectories!
def d_step_G23(a):
    # Returns (k, a_next, trace_of_x)
    if a % 2 == 1:
        m = (a - 1) // 2
        return 1, 3 * m + 3, [m]
    m = a // 2
    if m % 2 == 0:
        return 2, 9 * (m // 2) + 4, [m]
    x = (3 * m + 3) // 2
    xs = [m, x]
    k = 3
    while x % 2 == 1:
        x = (3 * x + 1) // 2
        xs.append(x)
        k += 1
    return k, 9 * (x // 2) + 1, xs

def d_step_G24(a):
    if a % 2 == 0:
        m = a // 2
        return 1, 3 * m + 2, [m]
    m = (a - 1) // 2
    if m % 2 == 0:
        return 2, 9 * (m // 2) + 7, [m]
    x = (3 * m + 5) // 2
    xs = [m, x]
    k = 3
    while x % 2 == 1:
        x = (3 * x + 1) // 2
        xs.append(x)
        k += 1
    return k, 9 * (x // 2) + 1, xs

print("=== Testing G#23from [1, 2, 25]; 3 ===")
d, a = 25, 3
step = 0
while d > 0:
    k, a_next, xs = d_step_G23(a)
    if d < k:
        print(f"  Underflow at d={d} < k={k}, a={a}, xs={xs}")
        break
    d -= k
    a = a_next
    step += 1
    print(f"  Step {step:02d}: [1, 2, {d}]; {a} (k={k})")

print("\n=== Testing G#24 from [1, 2, 1, 10]; 4 ===")
d, a = 10, 4
step = 0
while d > 0:
    k, a_next, xs = d_step_G24(a)
    if d < k:
        print(f"  Underflow at d={d} < k={k}, a={a}, xs={xs}")
        break
    d -= k
    a = a_next
    step += 1
    print(f"  Step {step:02d}: [1, 2, 1, {d}]; {a} (k={k})")

print("\n=== Testing G#24 from [1, 2, 0, 670]; 199 ===")
d, a = 670, 199
step = 0
while d > 0:
    k, a_next, xs = d_step_G24(a)
    if d < k:
        print(f"  Underflow at d={d} < k={k}, a={a}, xs={xs}")
        break
    d -= k
    a = a_next
    step += 1
    if step <= 10 or d <= 20:
        print(f"  Step {step:03d}: [1, 2, 0, {d}]; {a} (k={k})")
print(f"  Final state after {step} steps: d={d}, a={a} (mod 16 = {a % 16})")
