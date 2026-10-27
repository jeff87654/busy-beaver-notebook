"""Validate the 15-state candidate found by search_w3 (fixed C_REL gadget)."""
import sys
from tm import parse
from probe_e import craft3, read3

M15 = ('1RI0LL_1RA1RC_0LD1LG_0RE1LD_1RZ1RF_1LI0RM_1RM0LH_1LG1LH_1RN1RJ_'
       '1RE0LA_1RA0RF_1LH1LA_1RB1RM_1RZ0LO_0LK1LO')
T = parse(M15)


def run(m, tape, head, steps, q0='A', gap=1, stop_on_cfg=True, window=False):
    T = parse(m); q, pos = q0, head
    ev = []
    for s in range(1, steps + 1):
        sym = tape.get(pos, 0)
        t = T[ord(q) - 65][sym]
        if t is None or t[2] == 'Z':
            return ('HALT', s, ev, tape, pos, q)
        w, mv, nq = t
        tape[pos] = w; pos += mv; q = nq
        if stop_on_cfg:
            cfg = read3(tape, pos, q, gap)
            if cfg is not None:
                ev.append((s, cfg))
                if len(ev) > 60:
                    return ('EVMAX', s, ev, tape, pos, q)
    return ('TIME', steps, ev, tape, pos, q)


def show_tape(tape, pos, k=30):
    lo = min([min(tape) if tape else 0, pos]) - 1
    hi = max([max(tape) if tape else 0, pos]) + 1
    a = pos - k if pos - k > lo else lo
    b = pos + k if pos + k < hi else hi
    return ''.join(str(tape.get(i, 0)) for i in range(a, b + 1))


if __name__ == '__main__':
    print('--- crafted Ce3 checks ---')
    for gap in (1,):
        for (p, a, c, d, e) in [(3, 8, 0, 2, 2), (3, 8, 0, 3, 2), (3, 8, 0, 2, 3),
                                (3, 8, 0, 0, 2), (3, 8, 0, 0, 3), (3, 8, 0, 0, 1),
                                (3, 8, 0, 0, 0), (3, 8, 0, 1, 2)]:
            t, h = craft3(p, a, c, d, e, gap)
            kind, s, ev, t2, pos, q = run(M15, t, h, 3000, gap=gap)
            rets = [(ss, cc) for ss, cc in ev if cc]
            print((p, a, c, d, e), kind, s, 'returns:', rets[:4])
    print('--- blank tape ---')
    kind, s, ev, t2, pos, q = run(M15, {}, 0, 200000, stop_on_cfg=True)
    print('blank:', kind, 'steps', s, 'events', len(ev))
    for ss, cc in ev[:40]:
        print('  ', ss, cc)
