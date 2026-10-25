import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq')
import idle
M = sys.argv[1] if len(sys.argv) > 1 else "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
def parse(m):
    t = {}
    for i, g in enumerate(m.split('_')):
        for s in range(2):
            e = g[3*s:3*s+3]
            t[(chr(65+i), s)] = None if e[2] in '-HZ' else (int(e[0]), e[1], e[2])
    return t
T = parse(M)
def run(steps, show=None):
    tape = {}; pos = 0; q = 'A'; n = 0
    while n < steps:
        s = tape.get(pos, 0)
        tr = T[(q, s)]
        if tr is None: return ('HALT', n, q, s, tape, pos)
        w, d, q2 = tr
        tape[pos] = w; pos += 1 if d == 'R' else -1; q = q2; n += 1
        if show: show(n, q, tape, pos)
    return ('RUN', n, q, tape.get(pos,0), tape, pos)
def fmt(tape, pos, q):
    lo = min(list(tape) + [pos]); hi = max(list(tape) + [pos])
    s = ''
    for i in range(lo, hi + 1):
        if i == pos: s += f'[{q}]'
        s += str(tape.get(i, 0))
    return s
if __name__ == '__main__':
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
    def show(n, q, tape, pos):
        if n >= N - 0 and n <= N + 0: print(n, fmt(tape, pos, q))
    r = run(N)
    print(r[0], r[1], fmt(r[4], r[5], r[2]))
