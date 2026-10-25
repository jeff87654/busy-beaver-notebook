"""trace.py MACHINE RUNSPEC NSTEPS [from] : print every step: step state head-rel-to-right-end window"""
import sys, re
def parse_tok(t):
    if t.endswith('.'): return '1'*int(t[:-1])
    if '|' in t:
        o, rest = t.split('|', 1)
        z = 2 if rest == '' else int(rest[:-1])
        return '1'*int(o) + '0'*z
    return '1'*int(t) + '0'
def parse_seq(s, i=0):
    out = []
    while i < len(s) and s[i] != ')':
        if s[i] == ' ': i += 1; continue
        if s[i] == '(':
            u, i = parse_seq(s, i+1); i += 1
        else:
            j = i
            while j < len(s) and s[j] not in ' ^)': j += 1
            u = parse_tok(s[i:j]); i = j
        k = 1
        if i < len(s) and s[i] == '^':
            j = i+1
            while j < len(s) and s[j].isdigit(): j += 1
            k = int(s[i+1:j]); i = j
        out.append(u*k)
    return ''.join(out), i
def word(spec):
    w, _ = parse_seq(spec); return w.rstrip('0')
def tm(ms):
    T = {}
    for i, r in enumerate(ms.split('_')):
        for c in range(2):
            t = r[3*c:3*c+3]
            T[(i, c)] = None if t[0] == '-' else (int(t[0]), 1 if t[1] == 'R' else -1, ord(t[2])-65)
    return T
if __name__ == '__main__':
    M = tm(sys.argv[1]); w = word(sys.argv[2]); N = int(sys.argv[3]); fr = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    W = int(sys.argv[5]) if len(sys.argv) > 5 else 40
    tape = {i: int(c) for i, c in enumerate(w)}; p = len(w); q = 1
    for st in range(N):
        c = tape.get(p, 0)
        if st >= fr:
            R = max(k for k, v in tape.items() if v) if any(tape.values()) else 0
            lo = R - W
            s = ''.join(('[' if k == p else '') + str(tape.get(k, 0)) + (']' if k == p else '') for k in range(lo, R+4))
            print(f"{st:6d} {'ABCDEFGH'[q]}{c} {s}")
        t = M[(q, c)]
        if t is None: print('HALT', st); break
        tape[p] = t[0]; p += t[1]; q = t[2]
