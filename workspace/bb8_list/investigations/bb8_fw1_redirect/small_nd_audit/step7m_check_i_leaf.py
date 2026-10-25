from step5_analyze_probe_919 import rows

for r in rows:
    if r["m"] == "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1RH0LG_---0LE_0RA1RF":
        for a in range(1, 17):
            print(f"  E({a:2d}): {r['E'][a]}")

# Now let's trace Round 1 on the blank tape from @248: [3, 5, 5]; 5; 0!
# D(a) = 3a + 5
# B1([..., d, 0], a) = [..., d-2]; 9a + 15
a = 5
# [3, 5, 5]; 5 -> 5 D-steps:
for _ in range(5):
    a = 3 * a + 5
print(f"After [3, 5, 5] -> [3, 5, 0]: a = {a}")
# B1 on [3, 5, 0] -> [3, 3]:
a = 9 * a + 15
print(f"After B1 -> [3, 3]: a = {a}")
# 3 D-steps on [3, 3] -> [3, 0]:
for _ in range(3):
    a = 3 * a + 5
print(f"After [3, 3] -> [3, 0]: a = {a}")
# B1 on [3, 0] -> [1]:
a = 9 * a + 15
print(f"After B1 -> [1]: a = {a}")
# 1 D-step on [1] -> []:
a = 3 * a + 5
print(f"At E1(A1): A1 = {a}, A1 mod 4 = {a % 4}, A1 mod 2 = {a % 2}")
