"""Independent check (lead): champion rules R1-R3 on the rebuilt list Lambda(b), with the rebuild's tail in place.
Configurations = head in state B on the blank right of the word, word = 11 D(m1)..D(mk) (10)^r TAIL.
Rules on token values (m = 3d+1 for an ordinary digit, any m for the prefix tokens; borrowing lowers m by 3), with the
list nearest-first L = [m_k, ..., m_1], a-token m_a = 3a+1 (the last token), b from r = 3b+2:
  R1: a > 0              -> a - 1, b -> 2b + 2
  R2: a = 0, L[0] > 1    -> L[0] - 3, new a = 2b + 2, b = 0
  R3: a = 0, L[0..k-1] = 1 (zeros), L[k] > 1 -> L[k] - 3, L[k-1] := 3(2b+2)+1, the other zeros kept, a = 0, b = 0
  python verify_chain.py B NCONF                       # from the real rebuilt list Lambda(B)
  python verify_chain.py custom "m1,m2,...,mk" A B NCONF  # from a constructed list (tokens farthest first) with the same tail
At an exhausted list (all tokens 1 = zeros) the run is followed to a halt, a family configuration, or 5e7 steps.
"""
import re, sys
from verify_lambda import Sim, parse_tm, M11, D
TAIL = '111111110011111100111111001111110011111100111111001001'
def lam(b):
    return '11' + D(4) + D(21) + D(4) + D(17) + D(4) * (12 * b - 12) + D(1) + D(34) + '10' * 44 + TAIL
def parse(w):
    if not w.endswith(TAIL): return None
    m = re.fullmatch(r'11((?:(?:10)*1)*)((?:10)*)', w[:-len(TAIL)])
    if not m: return None
    ms = [len(t) // 2 for t in re.findall(r'((?:10)*)1', m.group(1))]
    r = len(m.group(2)) // 2
    if (r - 2) % 3 or (ms[-1] - 1) % 3: return None   # a and b keep the champion encoding
    return ms[:-1], (ms[-1] - 1) // 3, (r - 2) // 3        # list farthest-first, a, b
def predict(lst, a, b):
    # residue-class digits: token m has residue m % 3 (1 ordinary, 2 like D17, 0 like D21); value (m - res) // 3,
    # "zero" means m < 3, a borrow subtracts 3, a refill keeps the target token's residue
    L = list(reversed(lst))                                  # nearest first
    if a > 0: return lst, a - 1, 2 * b + 2, 'R1'
    k = 0
    while k < len(L) and L[k] < 3: k += 1
    if k == len(L): return None                              # list exhausted
    L[k] -= 3
    if k == 0: return list(reversed(L)), 2 * b + 2, 0, 'R2'
    L[k - 1] = 3 * (2 * b + 2) + L[k - 1]
    return list(reversed(L)), 0, 0, 'R3'
def word(lst, a, b):
    return '11' + ''.join(D(m) for m in lst) + D(3 * a + 1) + '10' * (3 * b + 2) + TAIL
def main():
    if sys.argv[1] == 'custom':
        lst = [int(x) for x in sys.argv[2].split(',')]; a, b, n = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
        w0 = word(lst, a, b); label = f'custom {lst} a={a} b={b}'
    else:
        b0, n = int(sys.argv[1]), int(sys.argv[2]); w0 = lam(b0); label = f'Lambda({b0})'
    sim = Sim(parse_tm(M11), w0, head=len(w0), state=1)
    confs = []
    def cb(step, s):
        p = parse(s)
        if p is not None and step > 0:
            confs.append((step, p))
            if len(confs) >= n: raise StopIteration
    try: sim.run(5 * 10 ** 8, 1, cb)
    except StopIteration: pass
    cur = parse(w0); bad = 0; tally = {}
    for step, nxt in confs:
        pr = predict(*cur)
        if pr is None or (pr[0], pr[1], pr[2]) != nxt:
            bad += 1; print(f'MISMATCH at step {step}: from {cur} predicted {pr} got {nxt}')
        else:
            tally[pr[3]] = tally.get(pr[3], 0) + 1
        cur = nxt
    if sim.halted:
        print(f'  HALT at step {sim.steps} (after the last configuration), ones {sim.ones()}')
    print(f'{label}: {len(confs)} consecutive configurations, rules applied {tally}, mismatches {bad}; '
          f'last: list {cur[0][:6]}..{cur[0][-4:]} a={cur[1]} b={cur[2]} at step {confs[-1][0] if confs else 0}')
if __name__ == '__main__': main()
