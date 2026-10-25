"""Mutation test: rebuild the hand-written spec.NG with ONE atom mutated (its two labels swapped, or
one label shifted); validate.check_rpn must then report a mismatch on every sample."""
import random, spec, validate

orig_wel, orig_weq, orig_NG = spec.wel, spec.weq, spec.NG

def build_mutant(k, mode):
    cnt = [0]
    def mut(f):
        def g(i, j):
            cnt[0] += 1
            if cnt[0] == k:
                return f(j, i) if mode == 'swap' else f(i, (j + 1) % 4)
            return f(i, j)
        return g
    spec.wel, spec.weq = mut(orig_wel), mut(orig_weq)
    try:
        return spec._ng(), cnt[0]
    finally:
        spec.wel, spec.weq = orig_wel, orig_weq

_, natoms = build_mutant(0, 'swap')
rnd = random.Random(5)
bad = 0; tried = 0
for k in rnd.sample(range(1, natoms + 1), 20):
    for mode in ('swap', 'shift'):
        m, _ = build_mutant(k, mode)
        if m == orig_NG:          # swapping x∈x-like or x=y symmetric pairs can be a no-op; skip
            continue
        spec.NG = m
        n = validate.check_rpn(random.Random(3), 20)
        tried += 1
        if n != 20:
            bad += 1; print('NOT CAUGHT', k, mode, n)
spec.NG = orig_NG
u = validate.check_rpn(random.Random(3), 50)
print(f'atom positions in spec.NG: {natoms}; mutants tried {tried}, not caught {bad}; unmutated mismatches {u}')
print('MUTATION OK' if bad == 0 and u == 0 else 'MUTATION FAIL')
