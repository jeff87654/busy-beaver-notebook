"""TNF prefix path of a machine, in the format of estimate_20260926/champion_neighborhood/path8.txt.

  python tnf_path.py MACHINE [NSTATES=8]

Simulates the target machine from the blank tape using only the transitions defined so far; each time an undefined
transition is met, it is copied from the target (as mxdys's TNF enumerator would branch there), and one line
"m PREFIX a b c" is printed (a = states in use incl. the next unused one, b = symbols in use, c = transitions left,
the arguments of knuth8.exe exactfrom/exactsplit/knuthfrom). Stops at the target's halt transition, or when the target
needs a state >= NSTATES (e.g. the BB(9) champion restricted to 8 states).
"""
import sys

def parse(tm):
    rows = tm.split('_')
    t = {}
    for q, r in enumerate(rows):
        for c in (0, 1):
            s = r[3 * c:3 * c + 3]
            t[(q, c)] = None if s[2] in '-Z' else (int(s[0]), 1 if s[1] == 'R' else -1, ord(s[2]) - 65)
    return t, len(rows)

def fmt(pre, n):
    out = []
    for q in range(n):
        for c in (0, 1):
            v = pre.get((q, c))
            out.append('---' if v is None else f"{v[0]}{'R' if v[1] > 0 else 'L'}{chr(65 + v[2])}")
    return '_'.join(''.join(out[2 * q:2 * q + 2]) for q in range(n))

def main():
    tm = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    full, _ = parse(tm)
    pre = {(0, 0): full[(0, 0)]}
    m = 1
    used_s, used_c = 2, 2
    print(m, fmt(pre, n), used_s, used_c, 2 * n - m)
    tape, pos, q, steps = {}, 0, 0, 0
    while steps < 10_000_000:
        c = tape.get(pos, 0)
        if (q, c) not in pre:
            v = full.get((q, c))
            if v is None or v[2] >= n:
                return
            pre[(q, c)] = v; m += 1
            used_s = min(n, max(used_s, v[2] + 1)); used_c = 2
            print(m, fmt(pre, n), used_s, used_c, 2 * n - m)
        w, d, nq = pre[(q, c)]
        tape[pos] = w; pos += d; q = nq; steps += 1

main()
