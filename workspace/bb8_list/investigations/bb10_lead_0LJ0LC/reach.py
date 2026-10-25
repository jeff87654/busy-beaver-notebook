"""How far left does one rule application read? Simulate a constructed N(...) to the next G right-end event and report
the leftmost head position, as (group index, offset) of the start word."""
import sys
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC'
T = {}
for qi, ch in enumerate(M.split('_')):
    for s in (0, 1):
        e = ch[3*s:3*s+3]
        T[('ABCDEFGHIJ'[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, e[2])
def word(ns):
    w = '1'; starts = []
    for n in ns:
        starts.append(len(w)); w += '10' * n + '1'
    return w, starts
def go(ns, maxs=10**7):
    w, starts = word(ns)
    off = 100
    tape = {i + off: int(c) for i, c in enumerate(w)}
    pos = off + len(w); q = 'G'; mn = pos; steps = 0
    while steps < maxs:
        s = tape.get(pos, 0); tr = T[(q, s)]
        if tr is None: return ('HALT', steps, mn - off)
        tape[pos] = tr[0]; pos += tr[1]; q = tr[2]; steps += 1
        mn = min(mn, pos)
        if q == 'G' and tape.get(pos, 0) == 0 and all(tape.get(i, 0) == 0 for i in range(pos + 1, pos + 50)):
            return ('EV', steps, mn - off, starts)
    return ('TIMEOUT',)
for ns in eval(sys.argv[1]):
    print(ns, go(ns))
