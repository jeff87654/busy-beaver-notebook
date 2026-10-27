import sys
from tm import run, tape_sig, ones

CORE13 = '1RI0LL_1RA1RC_0LD1LG_0RE1LD_1RZ1RF_1LI0RM_1RM0LH_1LG1LH_0LK1RJ_1RE0LA_1RA0RF_1LH1LA_1RB1RM'


def craft(p, A, d, c=0):
    # 0* (10)^p 1^(A+2) [head here] (10)^c 0 1^d 0*
    # head cell: first 1 of (10)^c if c>0, else the separator 0
    tape = {}
    pos = 10
    for _ in range(p):
        tape[pos] = 1
        tape[pos + 1] = 0
        pos += 2
    for _ in range(A + 2):
        tape[pos] = 1
        pos += 1
    start = pos
    if c > 0:
        for _ in range(c):
            tape[pos] = 1
            tape[pos + 1] = 0
            pos += 2
        tape[pos] = 0   # separator between c-block and d
        pos += 1
    else:
        tape[pos] = 0   # head cell is the separator
        pos += 1
    for _ in range(d):
        tape[pos] = 1
        pos += 1
    return tape, start


def trace(p, A, d, c=0, steps=120):
    tape, start = craft(p, A, d, c)
    print('start head=%d' % start, tape_sig(tape, start))
    T = {}
    from tm import parse
    T = parse(CORE13)
    q = 'A'
    pos = start
    seen = []
    for s in range(1, steps + 1):
        sym = tape.get(pos, 0)
        t = T[ord(q) - 65][sym]
        if t is None:
            print('%3d HALT(undef) q=%s' % (s, q)); break
        w, mv, nq = t
        tape[pos] = w
        pos += mv
        seen.append((s, q, sym, w, mv, nq, pos))
        if nq == 'Z':
            print('%3d HALT q=%s' % (s, q)); break
        q = nq
        if s % 1 == 0 and (s > 100 or q in 'AIJK'):
            print('%3d q=%s pos=%d %s' % (s, q, pos, tape_sig(tape, pos)))
    print('final', tape_sig(tape, pos), 'ones', ones(tape))


if __name__ == '__main__':
    trace(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 0,
          int(sys.argv[5]) if len(sys.argv) > 5 else 120)
