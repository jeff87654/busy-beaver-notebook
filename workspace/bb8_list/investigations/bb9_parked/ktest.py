"""ktest.py: literal next-K-moment probe for a template.  ktest.py MACHINE Q U S BETA tokens(far->near, comma) r
prints the next K-moment (tokens, r) or the halt / step-limit."""
import sys
def parse_tm(m):
    rows = m.split('_'); T = {}
    for q, r in enumerate(rows):
        for c in (0, 1):
            x = r[3*c:3*c+3]
            T[(q, c)] = None if ('-' in x) else (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return T
def run(m, Q, U, S, toks, r, maxs=10**7, P='1'):
    T = parse_tm(m)
    w = P + ''.join(U * x + '1' for x in toks) + U * r + S
    tape = dict((i, int(ch)) for i, ch in enumerate(w)); h = len(w); q = Q; last1 = max(i for i in tape if tape[i])
    for st in range(1, maxs):
        c = tape.get(h, 0); tr = T[(q, c)]
        if tr is None: return ('HALT', chr(65+q)+str(c), st)
        tape[h] = tr[0]
        if tr[0] and h > last1: last1 = h
        elif not tr[0] and h == last1:
            while last1 > -10**9 and not tape.get(last1, 0): last1 -= 1
        h += tr[1]; q = tr[2]
        if q == Q and tape.get(h, 0) == 0 and h > last1:
            s = ''.join(str(tape.get(i, 0)) for i in range(min(tape), h))
            if s.endswith(S):
                body = s[:-len(S)].lstrip('0')
                # parse from the right: U^r then tokens U^x 1
                rr = 0; b = body
                while b.endswith(U): b = b[:-len(U)]; rr += 1
                tk = []
                while b.endswith('1'):
                    b = b[:-1]; x = 0
                    while b.endswith(U): b = b[:-len(U)]; x += 1
                    tk.append(x)
                if tk and b.lstrip('0') in ('', P):
                    return ('K', st, list(reversed(tk)), rr, b)
    return ('LIMIT',)
if __name__ == '__main__':
    m, Q, U, S, beta = sys.argv[1], ord(sys.argv[2]) - 65, sys.argv[3], sys.argv[4], int(sys.argv[5])
    toks = [int(x) for x in sys.argv[6].split(',')]; r = int(sys.argv[7])
    print(run(m, Q, U, S, toks, r))
