import idle
import sys
X = "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE"
I = "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA0LG_---0LE"
def parse(s):
    T = {}
    for q, grp in enumerate(s.split('_')):
        for r in range(2):
            t = grp[3*r:3*r+3]
            if t[0] == '-': T[(q, r)] = None
            else: T[(q, r)] = (int(t[0]), 1 if t[1]=='R' else -1, ord(t[2])-65)
    return T
def rle(tape, pos, st):
    # print tape as string with head marker
    lo = min(tape) if tape else pos; hi = max(tape) if tape else pos
    lo = min(lo, pos); hi = max(hi, pos)
    s = ''
    for i in range(lo, hi+1):
        c = str(tape.get(i, 0))
        if i == pos: s += '[' + 'ABCDEFG'[st] + c + ']'
        else: s += c
    return s
def run(m, N, show=None):
    T = parse(m); tape = {}; pos = 0; st = 0
    for n in range(N):
        sym = tape.get(pos, 0)
        tr = T[(st, sym)]
        if tr is None: return ('HALT', n, st, sym, sum(tape.values()), tape, pos)
        w, d, ns = tr
        tape[pos] = w; pos += d; st = ns
        if show: show(n+1, tape, pos, st)
    return ('RUN', N, st, None, sum(tape.values()), tape, pos)
