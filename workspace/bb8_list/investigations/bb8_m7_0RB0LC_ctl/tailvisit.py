"""Experiment: head enters a tail word from the left (state q at tail[0]); run until it exits left; report result."""
import sys
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE'
T = {}
for i, r in enumerate(M.split('_')):
    for c in range(2):
        t = r[3*c:3*c+3]
        T[('ABCDEFGH'[i], c)] = None if t[0] == '-' else (int(t[0]), 1 if t[1] == 'R' else -1, t[2])
def visit(q, w, maxs=10**6):
    tape = [int(c) for c in w]; p = 0
    for st in range(maxs):
        if p < 0: return ('exit', q, ''.join(map(str, tape)).rstrip('0'), st)
        if p >= len(tape): tape.append(0)
        t = T[(q, tape[p])]
        if t is None: return ('HALT', q, ''.join(map(str, tape)), st)
        tape[p] = t[0]; p += t[1]; q = t[2]
    return ('timeout', q, ''.join(map(str, tape)).rstrip('0'), maxs)
def runs(w):
    import re
    return ' '.join(f'{len(m.group(1))}{"." if not m.group(2) else ("" if len(m.group(2))==1 else ("|" if len(m.group(2))==2 else "|"+str(len(m.group(2)))+"|"))}' for m in re.finditer(r'(1+)(0*)', w))
if __name__ == '__main__':
    for j in range(0, 3):
        w = '1'*8 + '00111111'*j + '001001'
        for q in 'ABDEFGH':
            res = visit(q, w)
            print(j, q, res[0], res[1], res[3], runs(res[2]) if res[0] != 'HALT' else res[2])
