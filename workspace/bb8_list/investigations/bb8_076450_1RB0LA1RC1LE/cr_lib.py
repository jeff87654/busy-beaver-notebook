"""Exact literal checks (no acceleration) of the rules of
1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_0RA0RG.

Ec(k, b, r) = 0^inf E>0 1 1 0 (1010)^k (01)^b r        (a = 2k+1 copies of 10 after the leading 1)
Phase rules (r arbitrary and never visited, unless it is 0^inf):
  IN : Ec(k, b+1, r)        -> Ec(k+1, b, r)
  S5 : Ec(k, 0, 11111 r)    -> Ec(2, 2k+2, r)
  S4 : Ec(k, 0, 1111 0^inf) -> Ec(2, 2k+1, 0^inf)
  Z0 : Ec(k, 0, 0^inf)      -> Ec(1, 0, 1^(4k+5) 0^inf)
  Z1 : Ec(k, 0, 1 0^inf)    -> Ec(1, 0, 1^(4k+7) 0^inf)     (only used before the family is entered)
Family (Fa(m,q,s) = Ec(5m+1, 0, (11111)^q s), s = 0^inf or 1111 0^inf; Fb(m) = Ec(5m, 0, 0^inf)):
  T1 : Fa(m, q+1, s)     -> Fa(2m+1, q, s)
  T2 : Fa(m, 0, 1111)    -> Fb(2m+1)
  T3 : Fa(m, 0, empty)   -> Fa(0, 4m+1, 1111)
  T4 : Fb(m)             -> Fa(0, 4m+1, empty)
Each run goes from the start to the FIRST later configuration with state E reading 0 and a blank tape to the
left whose word equals the target (for phase rules), or to the first later family configuration Ec(k,0,1^c)
(for family rules); the exact tape is compared and, for arbitrary r, no cell of r may be visited.
Usage: python check_rules.py [out.json]   (check_rules_variant.py imports run() from here)
"""
import json, random, sys
TM = "1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_0RA0RG"
ST = 'ABCDEFGH'

def table(tm):
    return [[None if ch[i:i+3] == '---' else (int(ch[i]), 1 if ch[i+1] == 'R' else -1, ST.index(ch[i+2]))
             for i in (0, 3)] for ch in tm.split('_')]

TT = table(TM)

def word(k, b, tail):
    return [1, 1, 0] + [1, 0, 1, 0] * k + [0, 1] * b + list(tail)

def run(start_word, target_word, rlen, maxsteps, is_target=None, TT=TT):
    """start: head (state E) on the blank cell left of start_word; r = last rlen cells of start_word (fixed).
    Returns (steps, ok, visited_r)."""
    N = 4 * len(start_word) + 4 * len(target_word or []) + 256
    tape = bytearray(N + len(start_word) + 64)
    base = N  # position of first cell of start_word
    for i, x in enumerate(start_word): tape[base + i] = x
    pos, st = base - 1, ST.index('E')
    rstart = base + len(start_word) - rlen
    end_fixed = base + len(start_word)  # cells >= end_fixed are blank (0^inf) or r continues as blank
    visited_r = False
    for s in range(1, maxsteps + 1):
        e = TT[st][tape[pos]]
        if e is None:
            return s - 1, 'HALT', visited_r
        tape[pos] = e[0]; pos += e[1]; st = e[2]
        if rlen and pos >= rstart: visited_r = True
        if pos <= 1 or pos >= len(tape) - 2: return s, 'OVERFLOW', visited_r
        if st == 4 and tape[pos] == 0 and not any(tape[:pos]):
            w = bytes(tape[pos + 1:])
            w = w.rstrip(b'\x00')
            if is_target is not None:
                res = is_target(list(w))
                if res is not None:
                    return s, res, visited_r
            elif list(w) == list(bytes(target_word).rstrip(b'\x00')):
                # also check absolute alignment: the target word ends at the same cell as the start word
                if rlen == 0 or pos + 1 + len(target_word) == end_fixed:
                    return s, True, visited_r
                return s, 'MISALIGNED', visited_r
    return maxsteps, 'TIMEOUT', visited_r

def parse_family1(w):
    if w[:3] != [1, 1, 0]: return None
    i = 3; k = 0
    while w[i:i+4] == [1, 0, 1, 0]: i += 4; k += 1
    rest = w[i:]
    if any(x != 1 for x in rest): return None
    return (k, len(rest))

def parse_family(w):
    """w = 1 1 0 (1010)^k 1^c (a list with trailing 0s stripped) -> (k, c) or None.
    A word with c = 0 ends in 0, which the stripping removed, so also try w + [0] (the two cases exclude each other)."""
    return parse_family1(w) or parse_family1(w + [0])

def main():
    random.seed(12345)
    out = {}; fails = 0; total = 0
    ctxs = [[], None, None]
    def rand_ctx():
        return [random.randint(0, 1) for _ in range(random.randint(1, 8))] + [1]
    # phase rules
    for k in range(0, 40):
        for ci in range(3):
            r = [] if ci == 0 else rand_ctx()
            cases = []
            for b in range(0, 4):
                cases.append(('IN', word(k, b + 1, r), word(k + 1, b, r), len(r)))
            cases.append(('S5', word(k, 0, [1]*5 + r), word(2, 2*k + 2, r), len(r)))
            if ci == 0:
                cases.append(('S4', word(k, 0, [1]*4), word(2, 2*k + 1, []), 0))
                cases.append(('Z0', word(k, 0, []), word(1, 0, [1]*(4*k + 5)), 0))
                cases.append(('Z1', word(k, 0, [1]), word(1, 0, [1]*(4*k + 7)), 0))
            for name, sw, tw, rl in cases:
                steps, ok, vis = run(sw, tw, rl, 10**6)
                good = (ok is True) and not vis
                total += 1
                if not good:
                    fails += 1
                    print('FAIL', name, 'k=%d' % k, 'ctx', r, ok, 'visited r' if vis else '', steps)
                out.setdefault(name, []).append(dict(k=k, ctx=''.join(map(str, r)), steps=steps, ok=good))
    # family rules
    def fam_target(kk, cc):
        def f(w):
            p = parse_family(w)
            if p is None: return None
            return p == (kk, cc)
        return f
    for m in range(0, 8):
        for q in range(0, 4):
            for sflag in (0, 1):
                s = [1]*4 if sflag else []
                k = 5*m + 1; c = 5*q + len(s)
                if q >= 1:
                    name, tk, tc = 'T1', 5*(2*m + 1) + 1, 5*(q - 1) + len(s)
                elif sflag:
                    name, tk, tc = 'T2', 5*(2*m + 1), 0
                else:
                    name, tk, tc = 'T3', 1, 5*(4*m + 1) + 4
                steps, ok, vis = run(word(k, 0, [1]*c), None, 0, 10**8, fam_target(tk, tc))
                total += 1
                if ok is not True:
                    fails += 1; print('FAIL', name, m, q, sflag, ok, steps)
                out.setdefault(name, []).append(dict(m=m, q=q, s=sflag, steps=steps, ok=ok is True))
        # T4
        steps, ok, vis = run(word(5*m, 0, []), None, 0, 10**8, fam_target(1, 5*(4*m + 1)))
        total += 1
        if ok is not True:
            fails += 1; print('FAIL T4', m, ok, steps)
        out.setdefault('T4', []).append(dict(m=m, steps=steps, ok=ok is True))
    for name in out:
        print('%-3s %d/%d ok' % (name, sum(1 for x in out[name] if x['ok']), len(out[name])))
    print('total %d cases, %d failures' % (total, fails))
    if len(sys.argv) > 1:
        json.dump(out, open(sys.argv[1], 'w'), indent=0)

if __name__ == '__main__':
    main()
