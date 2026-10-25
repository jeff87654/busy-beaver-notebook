"""f3check.py LOG...: projected-accumulator argument for rows whose exhaustion halts in one parity class and whose
plain invariant search fails (dl3 F3 family).  From the measured RULE lines of an audit2 log:
  D: A -> A + c ;  B_k: [.., y+1, 0^k, A] -> [.., y, R_k(A), t_k..., A'_k]
P(v) = A + c * d_last (mod 2) is the parity A will have when the last digit has run down.
Checks: (1) D keeps P;  (2) B1 keeps P (P' depends on A only through the refill: A'_1 + c*(A + e) == A mod 2);
(3) B2 sets P to a constant P2;  (4) for every measured k >= 3 the two last digits after B_k are nonzero and the third
last is nonzero (refill or tail), so the first time the two last positions are both zero a B2 follows (B2 decrements
position n-2, which nothing else touches); same for the rebuilt list;  hence the last multi-zero borrow before an
exhaustion is a B2 and X_E = P2 (mod 2).  (5) the exhaustion class X = P2 mod 2 does not halt (from the log)."""
import sys, re
from fractions import Fraction as Fr

def parse_entries(s):
    out = []
    for t in s.split():
        if t.startswith('['): return None          # symbolic block
        m = re.match(r'^(.*)\*(\d+)$', t)
        if m and 'X' not in m.group(1): out += [m.group(1)] * int(m.group(2)); continue
        out.append(t)
    return out

def lin(t):
    """'X1-8' -> (coefA, const) ; '3' -> (0, 3)"""
    t = t.replace('X1', 'A')
    if 'A' not in t: return (0, int(t))
    m = re.match(r'^(\d*)\*?A([+-]\d+)?$', t)
    if not m: return None
    a = int(m.group(1)) if m.group(1) else 1
    return (a, int(m.group(2) or 0))

for path in sys.argv[1:]:
    L = open(path).read().splitlines()
    rules = {}
    for l in L:
        m = re.search(r'RULE k=\s*(\d+): \[y\+(\d+),0\^\d+,A\] -> \[y, (.*)\]$', l)
        if m:
            e = parse_entries(m.group(3))
            if e is not None: rules[int(m.group(1))] = [lin(x) for x in e]
    halt = re.search(r'HALT classes \[([^\]]*)\]', '\n'.join(L))
    hc = [int(x) for x in halt.group(1).split(',') if x.strip()] if halt else []
    reb = [l for l in L if '   rebuild' in l]
    name = path.split('/')[-1].split('\\')[-1][:-4]
    try:
        c = rules[0][-1][1]; assert rules[0][-1][0] == 1
        ok = True; why = []
        if c % 2 == 0:
            # D keeps A mod 2.  B1 sets A to a constant; every B_k (k >= 2) leaves its last two digits nonzero, so a B1
            # (borrow over exactly one zero) follows it: the last borrow before an exhaustion is a B1 and X = A'_1 mod 2.
            A1 = rules[1][-1]
            if A1[0] != 0: ok = False; why.append("B1 A' depends on A")
            p1 = A1[1] % 2
            for k, new in rules.items():
                if k < 2: continue
                digs = new[:-1]
                if len(digs) < 2 or any(x[0] == 0 and x[1] == 0 for x in digs[-2:]): ok = False; why.append('k=%d zero in last two' % k)
            if any(h % 2 == p1 for h in hc): ok = False; why.append('class %d halts' % p1)
            print(name, 'c=%d (even) B1 sets A=%d halting parity %s' % (c, A1[1], sorted(set(h % 2 for h in hc))), 'rules k<=%d' % max(rules),
                  'CONFIRMED(last borrow before an exhaustion is B1; X_E = %d mod 2 never halts)' % p1 if ok else 'NOT SHOWN ' + '; '.join(why))
            for r in reb[:2]: print('   ', r.strip()[:120])
            continue
        # (1) D keeps P: P = A + c*d ; D: d-1, A+c -> same
        # (2) B1: new = [R, A'] : P' = A' + c*R(A) ; need P' == A (mod 2) for all A
        R1, A1 = rules[1][0], rules[1][-1]
        if A1[0] != 0: ok = False; why.append('B1 A\' depends on A')
        if (c * R1[0]) % 2 != 1 or (A1[1] + c * R1[1]) % 2 != 0: ok = False; why.append('B1 does not keep P')
        # (3) B2 constant P
        new2 = rules[2]; last2 = new2[-2]; A2 = new2[-1]
        if A2[0] or last2[0]: ok = False; why.append('B2 last digit/A depend on A')
        P2 = (A2[1] + c * last2[1]) % 2
        # (4) k >= 3: last two digits and third-last nonzero
        for k, new in rules.items():
            if k < 3: continue
            digs = new[:-1]
            if len(digs) < 3: ok = False; why.append('k=%d short' % k); continue
            for x in digs[-3:]:
                if x[0] == 0 and x[1] == 0: ok = False; why.append('k=%d zero in last three' % k)
        # (5) exhaustion class P2 does not halt (hc lists halting residues mod 720 among r < NCL)
        if P2 in [h % 2 for h in hc] and any(h % 2 == P2 for h in hc): ok = False; why.append('class P2=%d halts' % P2)
        print(name, 'c=%d P2=%d halting parity %s' % (c, P2, sorted(set(h % 2 for h in hc))), 'rules k<=%d' % max(rules),
              'CONFIRMED(last multi-zero borrow is B2; X_E = %d mod 2 never halts)' % P2 if ok else 'NOT SHOWN ' + '; '.join(why))
        for r in reb[:2]: print('   ', r.strip()[:120])
    except Exception as ex:
        print(name, 'ERROR', repr(ex))
