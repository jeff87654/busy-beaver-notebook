"""Probe variants of the 15-state candidate's N0 transition."""
from tm import parse
from probe_e import craft3, read3

BASE = ('1RI0LL_1RA1RC_0LD1LG_0RE1LD_1RZ1RF_1LI0RM_1RM0LH_1LG1LH_1RN1RJ_'
        '1RE0LA_1RA0RF_1LH1LA_1RB1RM_1RZ0LO_0LK1LO')


def mk(n0, n1=None):
    segs = BASE.split('_')
    segs[13] = n0 + (n1 if n1 else segs[13][3:])
    return '_'.join(segs)


def run(m, tape, head, steps, q0='A', gap=1, maxev=40):
    T = parse(m); q, pos = q0, head
    ev = []
    for s in range(1, steps + 1):
        sym = tape.get(pos, 0)
        t = T[ord(q) - 65][sym]
        if t is None or t[2] == 'Z':
            return ('HALT', s, ev)
        w, mv, nq = t
        tape[pos] = w; pos += mv; q = nq
        cfg = read3(tape, pos, q, gap)
        if cfg is not None:
            ev.append((s, cfg))
            if len(ev) >= maxev:
                return ('EVMAX', s, ev)
    return ('TIME', steps, ev)


if __name__ == '__main__':
    for n0 in ['1RZ', '1LO', '0LO', '1RO', '0RO', '1LK', '1RK', '0LK']:
        m = mk(n0)
        t, h = craft3(3, 8, 0, 0, 0, 1)
        k, s, ev = run(m, t, h, 800)
        t2, h2 = craft3(3, 8, 0, 0, 2, 1)
        k2, s2, ev2 = run(m, t2, h2, 800)
        bk, bs, bev = run(m, {}, 0, 3000)
        print(f"N0={n0}: e0 -> {k} {s} {ev[:2]} | e2 -> {k2} {s2} {ev2[:1]} | blank -> {bk} {bs} ev={bev[:3]}")
