import sys
from tm import parse, tape_sig, ones
from explore import CORE13, craft


def trace_all(p, A, d, c=0, steps=150):
    tape, start = craft(p, A, d, c)
    T = parse(CORE13)
    q, pos = 'A', start
    print('start', tape_sig(tape, pos))
    for s in range(1, steps + 1):
        sym = tape.get(pos, 0)
        t = T[ord(q) - 65][sym]
        if t is None:
            print('%4d HALT(undef) q=%s pos=%d' % (s, q, pos)); return
        w, mv, nq = t
        tape[pos] = w
        pos += mv
        print('%4d q=%s sym=%d w=%d %s nq=%s pos=%d | %s' % (s, q, sym, w, 'L' if mv < 0 else 'R', nq, pos,
              tape_sig(tape, pos, max(0, pos - 12), pos + 12)))
        if nq == 'Z':
            print('HALT'); return
        q = nq


if __name__ == '__main__':
    trace_all(*[int(x) for x in sys.argv[1:]])
