# Literal check of the final phase: from Kd [] 0 b (head on a 0, state D, 1^(b+1) to the right),
# run the champion until the halting transition E0 = 1RZ, apply it (write 1), and count ones.
M = '1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH'
T = {}
for i, row in enumerate(M.split('_')):
    for s in (0, 1):
        t = row[3*s:3*s+3]
        T[('ABCDEFGHI'[i], s)] = (int(t[0]), t[1], t[2])
for b in range(1, 22, 2):
    tape = {k: 1 for k in range(1, b + 2)}
    pos, q, steps = 0, 'D', 0
    while True:
        s = tape.get(pos, 0)
        w, d, nq = T[(q, s)]
        if nq == 'Z':
            ones_before = sum(tape.values())
            tape[pos] = w
            print(f'b={b}: ones at busycoq halt config = {ones_before} (b+3={b+3}), score incl. final write = {sum(tape.values())} (b+4={b+4})')
            break
        tape[pos] = w
        pos += 1 if d == 'R' else -1
        q = nq
        steps += 1
