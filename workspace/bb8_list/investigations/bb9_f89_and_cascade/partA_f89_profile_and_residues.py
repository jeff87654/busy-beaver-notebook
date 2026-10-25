import os, sys

F89_CODE = "1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE"

def parse_tm(code):
    parts = code.strip().split("_")
    trans = {}
    for s_idx, p in enumerate(parts):
        st = chr(ord('A') + s_idx)
        for sym in (0, 1):
            chunk = p[3*sym:3*sym+3]
            if chunk == "---":
                trans[(st, sym)] = None
            else:
                trans[(st, sym)] = (int(chunk[0]), -1 if chunk[1] == 'L' else 1, chunk[2])
    return trans

def check_k_config(tape, head, state, min_vis):
    if state != 'D' or head != min_vis:
        return None
    mx = max(tape.keys()) if tape else head
    bits = [tape.get(i, 0) for i in range(head, mx + 1)]
    while bits and bits[-1] == 0:
        bits.pop()
    if len(bits) < 4 or bits[0] != 0 or bits[1] != 0 or bits[2] != 0 or bits[3] != 1:
        return None
    i = 3
    L = []
    while i < len(bits):
        if bits[i] != 1:
            return None
        i += 1
        d = 0
        while i + 1 < len(bits) and bits[i] == 0 and bits[i+1] == 1:
            d += 1
            i += 2
        L.append(d)
    return L

print("=================================================================")
print("1. EXACT PRELUDE & ROUND-1 PROFILE OF F89, F89-S1, F89-S2, F89-S3")
print("=================================================================")

trans = parse_tm(F89_CODE)

for label, start_st, checkpoints in [
    ("F89-S3 (start D)", 'D', [13, 72, 408, 1311]),
    ("F89-S1 (start C)", 'C', [162, 322, 1019]),
    ("F89-S2 (start F)", 'F', [162, 322, 1019]),
    ("F89    (start A)", 'A', [89, 965, 4679]),
]:
    tape = {}
    head = 0
    st = start_st
    min_vis = 0
    slots_used = set()
    pairs_used = set()
    c0_hits = 0
    b00_hits = 0
    c00_hits = 0
    c01_hits = 0
    g00_hits = 0
    print(f"\n--- {label} ---")
    max_s = checkpoints[-1]
    for step in range(1, max_s + 1):
        cur = tape.get(head, 0)
        slot = f"{st}{cur}"
        slots_used.add(slot)
        w, d, nxt = trans[(st, cur)]
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d
        st = nxt
        nxt_sym = tape.get(head, 0)
        pair = f"{slot}:{nxt_sym}"
        pairs_used.add(pair)
        if slot == "C0": c0_hits += 1
        if pair == "B0:0": b00_hits += 1
        if pair == "C0:0": c00_hits += 1
        if pair == "C0:1": c01_hits += 1
        if pair == "G0:0": g00_hits += 1
        if head < min_vis:
            min_vis = head
        if step in checkpoints:
            L = check_k_config(tape, head, st, min_vis)
            all_14 = {f"{chr(ord('A')+i)}{b}" for i in range(7) for b in (0, 1)}
            unused_slots = sorted(all_14 - slots_used)
            print(f"  At step {step:4d} (K={L if L and len(L)<=6 else (f'[1^{len(L)}]' if L else None)}):")
            print(f"    unused slots (of 14): {unused_slots}")
            print(f"    S-only counts so far: C0={c0_hits}, B0:0={b00_hits}, C0:0={c00_hits}, C0:1={c01_hits}, G0:0={g00_hits}")

print("\n=================================================================")
print("2. EXACT p-ADIC RESIDUE LAW OF x(n) AFTER COLLAPSING [1^n] IN F89")
print("=================================================================")
# Let's verify our exact recursion:
#   f_0(a) = a + 4
#   f_1(a) = 2*a + 7
#   f_2(a) = 2^((a+9)//2) - 7
#   f_k(a) = f_{k-1}^((a+3)//2)(1)
# And for [1^n] (n >= 2):
#   x(n) = f_0(f_1(f_2(...f_{n-2}(1)...)))
# Let's check n = 1, 2, 3, 4, 5 exactly and modulo P for n >= 6!

def sim_abstract_f89(L):
    L = list(L)
    steps = 0
    while len(L) > 1:
        steps += 1
        if L[1] >= 3:
            # D
            m = (L[1] - 1) // 2
            L[0] += 4 * m
            L[1] = 1
        else:
            # Count k ones after L[0]
            k = 0
            while 1 + k < len(L) and L[1 + k] == 1:
                k += 1
            if 1 + k == len(L):
                # T_k: [a, 1^k] -> [1^(k-1), a+4]
                a = L[0]
                L = [1]*(k - 1) + [a + 4]
            else:
                # B_k: [a, 1^k, d, R] -> [1^k, a+4, d-2, R]
                a = L[0]
                d = L[1 + k]
                L = [1]*k + [a + 4, d - 2] + L[2 + k:]
    return L[0], steps

for n in (1, 2, 3, 4):
    x_val, m_steps = sim_abstract_f89([1]*n)
    print(f"  Exact [1^{n}] -> [{x_val}] in {m_steps} abstract steps")

# For n = 5: [1^5] -> [1, 1, 1, 5] -> ... -> f_0(f_1(f_2(f_3(1))))
# Wait: for n = 1: x = 1
# For n = 2: [1, 1] -> T_1 -> [5] (x = 5 = f_0(1))
# For n = 3: [1, 1, 1] -> [13] (x = 13 = f_0(f_1(1)))
# For n = 4: [1, 1, 1, 1] -> [61] (x = 61 = f_0(f_1(f_2(1))) = 2^6 - 3 = 61)
# For n = 5: x(5) = f_0(f_1(f_2(f_3(1)))). What is f_3(1)?
#   f_3(1) = f_2^((1+3)//2)(1) = f_2(f_2(1)) = f_2(25) = 2^((25+9)//2) - 7 = 2^17 - 7 = 131065!
#   Then x(5) = 2^((131065 + 11)//2) - 3 = 2^65538 - 3!
print("  For n = 5: f_3(1) = f_2(f_2(1)) = f_2(25) = 2^17 - 7 = 131,065")
print("             x(5) = 2^65538 - 3")

# And what is x(n) mod P for n >= 5?
# Notice that for n = 5, the exponent of 2 in x(5) = 2^E - 3 is E = 65538 = 2^16 + 2!
# And for ALL n >= 5:
#   f_3(a) = f_2^((a+3)//2)(1). Since a >= 1 is odd, (a+3)//2 >= 2, so the last two applications are
#   f_2(f_2(u)) where u >= 1 is odd!
#   Wait: u = 1 (when (a+3)//2 == 2, i.e., a = 1) or u = 2^((w+9)//2) - 7 (when (a+3)//2 >= 3)!
#   Wait: for n >= 6, x(n) = f_0(f_1(f_2(f_3(y)))) where y = f_4(...) >= 25 > 1!
#   In fact, for ANY tower [d_1, ..., d_n] with n >= 5:
#   Let's compute x(n) mod P for n = 1, 2, 3, 4, 5, and n >= 6!
for P in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 24, 30, 32, 36):
    r1 = 1 % P
    r2 = 5 % P
    r3 = 13 % P
    r4 = 61 % P
    r5 = (pow(2, 65538, P) - 3) % P
    # For n >= 6: y = f_2(u) = 2^((u+9)//2) - 7, and we apply f_2 at least 3 times:
    # Let's iterate the exact map u -> 2^((u+9)//2) - 7 using modular totient tower!
    def tower_f2_mod(depth, mod):
        if mod == 1:
            return 0
        if depth == 0:
            return 1 % mod
        # We need (u + 9) // 2 mod phi(mod) ... wait: simplest is to compute u = f_2(f_2(1)) = 131065,
        # and then f_2(131065) = 2^(65537) - 7, and then x = 2^(2^65536 + 2) - 3!
        # Wait: in f_3(1) = f_2(f_2(1)) = 131065, that's 2 applications of f_2.
        # In f_3(25) = f_2^14(1), that's 14 applications of f_2!
        # Let's compute exact f_2^m(1) for m = 1, 2, 3, 4, 5, 6 mod M!
        pass
    # Notice we can compute exact f_2^m(1) mod M for any M by递归 totient, because
    # (f_2(u) + 9) // 2 = 2^((u+7)//2) + 1, so let e_m = (f_2^m(1) + 7) // 2:
    #   e_0 = (1 + 7) // 2 = 4
    #   e_1 = (25 + 7) // 2 = 16 = 2^4
    #   e_2 = (131065 + 7) // 2 = 65536 = 2^16 = 2^(e_1)?
    # WAIT A SECOND!
    # Check that!!
    # Is (f_2(u) + 7) // 2 == 2^((u + 7) // 2) ?!
    # f_2(u) = 2^((u + 9)//2) - 7
    # f_2(u) + 7 = 2^((u + 9)//2)
    # (f_2(u) + 7) // 2 = 2^((u + 9)//2 - 1) = 2^((u + 7)//2) !!
    # AND x = f_0(f_1(f_2(u))) = 2^((u + 11)//2) - 3 = 4 * 2^((u + 7)//2) - 3 !!
    r6 = (4 * pow(2, 65536, P) - 3) % P
    print(f"  mod {P:2d}: x(1)={r1:2d}, x(2)={r2:2d}, x(3)={r3:2d}, x(4)={r4:2d}, x(5)={r5:2d}, x(>=6)={r6:2d}")
