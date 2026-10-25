"""Literal check of the halting ones count (independent of Coq).
Builds Kc ds a b exactly as in BB8_champ35_1RB0RA.v, runs the machine until the undefined E0, and counts ones
(before the halting write; the standard score adds 1).  Expect 24 b + 2 L + 36 for an all-zero list of L digits,
and for Kc [1] 0 0 the chain R2, R1, R1 gives b = U 0 0 = 6, so 24*6 + 2 + 36 = 182."""
M = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF"
T = {}
for i, grp in enumerate(M.split('_')):
    for s in (0, 1):
        t = grp[3*s:3*s+3]
        T[('ABCDEFGH'[i], s)] = None if t == '---' else (int(t[0]), 1 if t[1] == 'R' else -1, t[2])

def kc(ds, a, b):
    left = [1, 0, 1, 0, 1] + [1, 0] * (3*b+1) + [1] + [1, 0] * (3*a+1) + [1]
    for d in ds:
        left += [1, 0] * (3*d+1) + [1]
    tape = {}
    for i, s in enumerate(left):      # left[0] is the cell just left of the head
        tape[-1-i] = s
    return tape

def run(tape, q='G', pos=0, limit=10**8):
    steps = 0
    while True:
        s = tape.get(pos, 0)
        tr = T[(q, s)]
        if tr is None:
            return steps, sum(tape.values()), s
        w, d, q = tr
        tape[pos] = w; pos += d; steps += 1
        if steps > limit:
            raise RuntimeError('limit')

bad = 0
for L in range(1, 4):
    for b in range(0, 6):
        st, n, s = run(kc([0]*L, 0, b))
        ok = (n == 24*b + 2*L + 36 and s == 0)
        bad += not ok
        print(f'L={L} b={b}: steps={st} ones={n} head={s} expected={24*b+2*L+36} {"ok" if ok else "MISMATCH"}')
st, n, s = run(kc([1], 0, 0))
print(f'Kc [1] 0 0: steps={st} ones={n} head={s} expected=182 {"ok" if n == 182 else "MISMATCH"}')
bad += n != 182
print('ALL OK' if bad == 0 else f'{bad} MISMATCHES')
