# literal simulator, dict tape
M = "1RB1RC_0RC0LB_0RD1RF_1LE1LD_1RC1LG_1LD1RA_1LA0LH_---1LG"
QS = 'ABCDEFGH'
def parse(m):
    T = {}
    for qi, ch in enumerate(m.split('_')):
        for s in (0, 1):
            e = ch[3*s:3*s+3]
            T[(QS[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1]=='R' else -1, e[2])
    return T
T = parse(M)
def run(steps, tape=None, pos=0, q='A', cb=None):
    tape = {} if tape is None else tape
    for i in range(steps):
        s = tape.get(pos, 0)
        tr = T[(q, s)]
        if tr is None:
            return ('halt', i, tape, pos, q)
        w, d, nq = tr
        tape[pos] = w
        pos += d
        q = nq
        if cb: cb(i+1, tape, pos, q)
    return ('run', steps, tape, pos, q)
def show(tape, pos, q):
    ks = [k for k, v in tape.items() if v] + [pos]
    lo, hi = min(ks), max(ks)
    out = []
    for p in range(lo, hi+1):
        if p == pos: out.append('[' + q + ']')
        out.append(str(tape.get(p, 0)))
    return ''.join(out)
