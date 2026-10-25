import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

# Exact modular evaluation of K(d_k, ..., d_1; a; 0) -> K(0^k; A_final; 0) mod 2^r!
# Rules:
#   D:  (..., d+1; a) -> (..., d; 3a+3)
#   Bm: (..., y+1, 0^m; a) -> (..., y, 3a+3-m, 1^(m-1); 1)
#
# Notice that to know A_final mod 2^r, we need:
#   D^d(a) mod 2^r = (3^d * (a + 3/2) - 3/2) mod 2^r,
# which depends on (a mod 2^r) and (d mod 2^(r-1)) [since 3^(2^(r-1)) == 1 mod 2^(r+1) for r >= 2, and for r=1, 3^1 == 3 mod 4 so d mod 1 or d mod 2].
# To be 100% conservative, 3^(2^r) == 1 mod 2^(r+2), so D^d(a) mod 2^r depends ONLY on (a mod 2^r) and (d mod 2^r)!

from functools import lru_cache

def eval_D_pow(d_mod, a_mod, r):
    # Compute ((3^d_mod * (2*a_mod + 3) - 3) // 2) mod 2^r
    mod_2r = 1 << r
    mod_2r1 = 1 << (r + 1)
    p = pow(3, d_mod, mod_2r1)
    val = ((p * (2 * a_mod + 3) - 3) // 2) % mod_2r
    return val

# Let's first verify our exact recurrence against direct step-by-step K-level simulation on small lists!
def sim_K_exact(ds, a):
    ds = list(ds)
    while any(x > 0 for x in ds):
        if ds[-1] > 0:
            d = ds[-1]
            a = ((3**d) * (2*a + 3) - 3) // 2
            ds[-1] = 0
        else:
            # find rightmost non-zero
            m = 0
            idx = len(ds) - 1
            while ds[idx] == 0:
                m += 1
                idx -= 1
            ds[idx] -= 1
            ds[idx + 1] = 3*a + 3 - m
            for j in range(idx + 2, len(ds)):
                ds[j] = 1
            a = 1
    return a

# Recursive modular evaluator:
# clear_suffix(m, a_mod, r):
# Starting from suffix 0^m and accumulator a_mod (mod 2^r), Wait:
# A suffix of zeros 0^m is already cleared!
# What we want is: given a configuration (d_k, ..., d_1; a) where all d_i are small or given mod 2^r,
# define step_clear(j, a_mod, r) = the resulting a' mod 2^r after executing ONE borrow B_j from digit d_{j+1}
# (where digits j..1 are currently 0^j) and then completely clearing digits j..1 back to 0^j!
# Wait: when digits j..1 are 0^j and we decrement d_{j+1} via B_j:
#   B_j sets digits (j..1) to (3*a + 3 - j, 1, 1, ..., 1) and sets a = 1!
#   Then clearing digits (j..1) back to 0^j from (3*a + 3 - j, 1^(j-1); a=1) depends ONLY on (j, a mod 2^r, r)!

@lru_cache(maxsize=None)
def clear_tuple_mod(ds_tuple, a_mod, r):
    # Clear the tuple ds_tuple = (d_m, ..., d_1) where each d_i is given mod 2^r, starting from a_mod (mod 2^r).
    mod_2r = 1 << r
    if len(ds_tuple) == 0:
        return a_mod % mod_2r
    if len(ds_tuple) == 1:
        return eval_D_pow(ds_tuple[0] % mod_2r, a_mod % mod_2r, r)
    # First clear the lower (m-1) digits:
    a_cur = clear_tuple_mod(ds_tuple[1:], a_mod, r)
    # Now the state is (d_m, 0, ..., 0; a_cur). We must decrement d_m (which is ds_tuple[0] mod 2^r) to 0.
    # Each decrement of d_m applies the map f(a) = one_borrow_and_clear(m-1, a, r) on Z / 2^r Z!
    m_minus_1 = len(ds_tuple) - 1
    d_m = ds_tuple[0] % mod_2r
    return apply_borrow_pow(m_minus_1, d_m, a_cur, r)

@lru_cache(maxsize=None)
def one_borrow_and_clear(j, a_mod, r):
    # digits j..1 are 0^j (j >= 1). Apply B_j from d_{j+1} and clear digits j..1 back to 0^j.
    mod_2r = 1 << r
    first_d = (3 * a_mod + 3 - j) % mod_2r
    sub_tuple = (first_d,) + (1,) * (j - 1)
    return clear_tuple_mod(sub_tuple, 1, r)

@lru_cache(maxsize=None)
def apply_borrow_pow(j, count_mod, a_mod, r):
    # Apply `one_borrow_and_clear(j, ., r)` exactly `count_mod` times?
    # WAIT: What is the period of `one_borrow_and_clear(j, ., r)` on Z / 2^r Z?
    # Let's check! If its cycle length divides 2^r, then count_mod (mod 2^r) is enough!
    # Wait: what if `one_borrow_and_clear(j, ., r)` has a preperiod or cycle length not dividing 2^r?
    # That's why we check `one_borrow_and_clear(j, a_mod, r)` as a function of a_mod on Z / 2^r Z!
    cur = a_mod
    for _ in range(count_mod):
        cur = one_borrow_and_clear(j, cur, r)
    return cur

# Let's inspect `one_borrow_and_clear(j, a_mod, r)` for r = 1, 2, 3, 4 and j = 1..20!
for r in [1, 2, 3, 4]:
    mod_2r = 1 << r
    print(f"\n=== r = {r} (mod {mod_2r}) ===")
    for j in range(1, 10):
        table = [one_borrow_and_clear(j, a, r) for a in range(mod_2r)]
        print(f"  j={j:2d}: f(a) = {table}")
