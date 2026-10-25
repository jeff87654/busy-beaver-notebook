"""Unit test of the 1.q gadget alone (random register files, random selector position k, random gap).
Start: head on the cell after the chain ones, state 1.q, tape  1^(k+1) [0] 0^g  RF  with the 00 selector
left of R_k (register k = (k+1)-th run from the right).  Run until state 6.break.0 and check:
  head on the last chain one, all cells between it and the RF zero (marker cleared),
  RF = Q(k) applied to the register list (merge if R_{k+1}==0 else insert), no 00 left in the RF,
  left end of the RF unchanged (gap untouched).
usage: python gadget_test.py MACHINE.tm [cases]"""
import sys, random
from tmsim import load

def rf_cells(regs, k):
    s = ''
    for i in range(len(regs) - 1, -1, -1):
        s += '1' * (regs[i] + 1)
        if i > 0: s += '00' if i - 1 == k else '0'
    return s

def qmodel(regs, k):
    r = list(regs)
    if r[k + 1] == 0: r[k] += 3; del r[k + 1]
    else: r.insert(k + 1, 0)
    return r

def main():
    start, tbl = load(sys.argv[1]); n = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    rng = random.Random(5); bad = 0; nm = ni = 0
    for t in range(n):
        nreg = rng.randrange(2, 14); k = rng.randrange(0, nreg - 1)
        regs = [rng.choice([0, 0, 1, 2, rng.randrange(0, 9)]) for _ in range(nreg)]
        g = rng.randrange(2, 6)
        tape = {}
        for i in range(k + 1): tape[i] = '1'          # chain ones, positions 0..k
        p = k + 1                                     # head here (a 0), marker goes here
        rfs = rf_cells(regs, k); base = p + 1 + g
        for i, c in enumerate(rfs): tape[base + i] = c
        pos, st, steps = p, '1.q', 0
        while st != '6.break.0' and steps < 100000:
            w, d, st2 = tbl[(st, tape.get(pos, '0'))]
            tape[pos] = w; pos += 1 if d == 'R' else -1; st = st2; steps += 1
        exp = qmodel(regs, k)
        if exp != regs and regs[k + 1] == 0: nm += 1
        else: ni += 1
        cells = ''.join(tape.get(i, '0') for i in range(0, max(tape) + 1))
        ok = st == '6.break.0' and pos == k and cells[:k + 1] == '1' * (k + 1) \
            and set(cells[k + 1:base]) <= {'0'} and cells[base] == '1'
        got = [len(r) - 1 for r in cells[base:].strip('0').split('0')][::-1] if ok else None
        if '00' in cells[base:].strip('0'): ok = False
        if not ok or got != exp:
            bad += 1
            if bad <= 5: print('FAIL', regs, k, g, '->', got, 'exp', exp, st, pos)
    print(f'gadget 1.q: {n} cases ({nm} merges, {ni} inserts), failures {bad}')
    return bad

if __name__ == '__main__':
    sys.exit(1 if main() else 0)
