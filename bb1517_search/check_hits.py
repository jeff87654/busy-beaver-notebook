"""Check HIT_STOP machines printed by search_w3b

Self-contained (no imports from earlier throwaway scripts):
  * parse / tape builder / canonical return reader -- an independent
    re-implementation of search_w3b.cpp's harness;
  * check() -- a re-implementation of the nine tests;
  * blank-tape orbit under ordinary bbchallenge semantics ('---' and '1RZ' halt);
  * gadget trace: at every E0 (the entry into the N/O/P/Q gadget) record what
    the next state reads.  A real third counter must read 1 at every entry
    until it halts; a one-shot gadget reads 1 once and then 0.

usage:
  python3 check_hits.py FILE                 # all HIT_STOP lines in FILE
  python3 check_hits.py FILE --trace M p a d e maxs
"""
import sys

TESTS = [(3, 8, 2, 2), (3, 8, 3, 2), (3, 8, 2, 3), (3, 6, 2, 2),
         (3, 8, 0, 0), (3, 8, 1, 1), (3, 8, 1, 2), (3, 8, 1, 3), (3, 6, 0, 0)]
GAP = 2
DD = 2
MAXC = 2000
BLANK_CAP = 2_000_000


def parse(s):
    m = []
    for tok in s.split('_'):
        m.append(tok[0:3])
        m.append(tok[3:6])
    return m


def build_tape(p, a, d, e, gap=GAP):
    tape = {}
    idx = 60
    for _ in range(p):
        tape[idx] = 1; idx += 1; tape[idx] = 0; idx += 1
    for _ in range(a + 2):
        tape[idx] = 1; idx += 1
    pos = idx; tape[idx] = 0; idx += 1
    for _ in range(d):
        tape[idx] = 1; idx += 1
    tape[idx] = 0; idx += 1
    for _ in range(gap - 1):
        tape[idx] = 0; idx += 1
    for _ in range(e):
        tape[idx] = 1; idx += 1
    return tape, pos


def read_ret(tape, pos, gap=GAP):
    if not (tape.get(pos, 0) == 1 and tape.get(pos + 1, 0) == 0):
        return None
    i = pos - 1; ones_a = 0
    while i >= -MAXC and tape.get(i, 0) == 1:
        ones_a += 1; i -= 1
    if ones_a < 2 or (ones_a & 1):
        return None
    p_out = 0
    while i >= 0 and tape.get(i, 0) == 0 and tape.get(i - 1, 0) == 1:
        p_out += 1; i -= 2
    if i < 0:
        return None
    if any(tape.get(k, 0) for k in range(-MAXC, i + 1)):
        return None
    j = pos; c_out = 0
    while tape.get(j, 0) == 1 and tape.get(j + 1, 0) == 0:
        c_out += 1; j += 2
    if c_out < 1 or tape.get(j, 0) != 0:
        return None
    j += 1
    d_out = 0
    while tape.get(j, 0) == 1:
        d_out += 1; j += 1
    if tape.get(j, 0) != 0:
        return None
    j += 1
    for _ in range(1, gap):
        if tape.get(j, 0) != 0:
            return None
        j += 1
    e_out = 0
    while tape.get(j, 0) == 1:
        e_out += 1; j += 1
    if any(tape.get(k, 0) for k in range(j, j + MAXC)):
        return None
    return (p_out, ones_a - 2, c_out, d_out, e_out)


def run(m, p, a, d, e, gap=GAP, maxs=1200):
    """First canonical return / halt, plus the full event list."""
    tape, pos = build_tape(p, a, d, e, gap)
    st = 0
    events = []
    for step in range(1, maxs + 1):
        sym = tape.get(pos, 0)
        w, mv, ns = m[st * 2 + sym]
        if w == '-' or ns == 'Z':
            return ('HALT', step, pos, st, events)
        tape[pos] = int(w)
        pos += -1 if mv == 'L' else 1
        st = ord(ns) - ord('A')
        if st == 0:
            r = read_ret(tape, pos, gap)
            if r:
                events.append((step, r))
                return ('RET', step, pos, st, events)
    return ('TIMEOUT', maxs, pos, st, events)


def kind_of(m, t, maxs=2000):
    r = run(m, *t, maxs=maxs)
    if r[0] == 'RET':
        return 3, r[4][0][1]
    if r[0] == 'HALT':
        return 2, None
    return 1, None


def checks(m):
    prev = {}
    out = []
    for i, t in enumerate(TESTS):
        p, a, d, e = t
        k, r = kind_of(m, t)
        out.append((i, k, r))
        if k == 1:
            return False, out
        if i == 0:
            good = (k == 3 and r[3] == d - DD and r[4] == e
                    and r[1] >= 2 and r[1] % 2 == 0 and r[2] >= a // 2 + 1)
        elif i == 1:
            good = (k == 3 and r[3] == d - DD and r[4] == e and r[1] >= 2 and r[1] % 2 == 0
                    and r[0] == prev[0][0] and r[1] == prev[0][1]
                    and r[2] == prev[0][2] and r[4] == prev[0][4])
        elif i == 2:
            good = (k == 3 and r[3] == d - DD and r[4] == e and r[1] >= 2 and r[1] % 2 == 0
                    and r[0] == prev[0][0] and r[1] == prev[0][1]
                    and r[2] == prev[0][2] and r[3] == prev[0][3])
        elif i == 3:
            good = (k == 3 and r[3] == d - DD and r[4] == e and r[1] >= 2 and r[1] % 2 == 0
                    and r[0] == prev[0][0] and r[1] == prev[0][1]
                    and r[2] < prev[0][2] and r[2] >= a // 2 + 1)
        elif i == 4:
            good = k == 3 and r[2] >= 1 and r[3] >= 3 and r[3] % 2 == 1 and r[4] >= 1
        elif i == 5:
            good = k == 2
        elif i == 6:
            good = k == 3 and r[4] == 1 and r[2] >= 1 and r[3] >= 3 and r[3] % 2 == 1
        elif i == 7:
            good = (k == 3 and r[4] == 2 and r[0] == prev[6][0] and r[1] == prev[6][1]
                    and r[2] == prev[6][2] and r[3] == prev[6][3])
        elif i == 8:
            good = (k == 3 and r[2] >= 1 and r[3] >= 3 and r[3] % 2 == 1 and r[4] >= 1
                    and r[4] < prev[4][4] and prev[4][4] >= 4)
        else:
            good = False
        if not good:
            return False, out
        prev[i] = r
    return True, out


def blank_orbit(m, cap=BLANK_CAP):
    tape = {}
    pos = 0
    q = 0
    for step in range(1, cap + 1):
        t = m[q * 2 + tape.get(pos, 0)]
        if t[0] == '-' or t[2] == 'Z':
            return ('HALT', step, pos, q, tape)
        w, mv, ns = t
        tape[pos] = int(w)
        pos += -1 if mv == 'L' else 1
        q = ord(ns) - ord('A')
    return ('TIME', cap, pos, q, tape)


def ones(tape):
    return sum(1 for v in tape.values() if v == 1)


def gadget_view(m, p, a, d, e, gap=GAP, cap=1_000_000):
    """(step, symbol read right after entering the gadget at E0)."""
    tape, pos = build_tape(p, a, d, e, gap)
    st = 0
    out = []
    pending = False
    for step in range(1, cap + 1):
        sym = tape.get(pos, 0)
        if pending:
            out[-1] = (out[-1][0], sym)
            pending = False
        w, mv, ns = m[st * 2 + sym]
        if w == '-' or ns == 'Z':
            return ('HALT', step, out)
        if st == 4 and sym == 0:
            out.append((step, None))
            pending = True
        tape[pos] = int(w)
        pos += -1 if mv == 'L' else 1
        st = ord(ns) - ord('A')
    return ('TIME', cap, out)


def machines_from(fn):
    lines = [l.rstrip('\n') for l in open(fn) if 'HIT_STOP' in l]
    return [l[l.index('] ') + 2: l.index(' | ')] for l in lines]


def main():
    fn = sys.argv[1]
    ms = machines_from(fn)
    print(f"{len(ms)} HIT_STOP lines, {len(set(ms))} distinct")
    allok = True
    for k, s in enumerate(ms):
        m = parse(s)
        ok, out = checks(m)
        allok &= ok
        vals = [d[2] for d in out if len(d) == 3]
        kinds = [d[1] for d in out if len(d) == 3]
        print(f"\nm{k}: tests {'PASS' if ok else 'FAIL'}  k={kinds}")
        print(f"   {vals}")
        st, step, pos, q, tape = blank_orbit(m)
        print(f"   blank: {st} steps={step} ones={ones(tape)} state={chr(65 + q)}")
        gst, gstep, g = gadget_view(m, 3, 8, 1, 2)
        print(f"   gadget entries (d=1,e=2): {gst} steps={gstep} {g}")
    print("\nALL PASS" if allok else "\nSOME FAIL")


if __name__ == '__main__':
    main()
