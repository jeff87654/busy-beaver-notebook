"""Independent check (lead session) of the possible BB(9) record's rebuild and of the rules on the rebuilt list.

Machine #11: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---   (twin #12: ..._0RH0RE_0LH---)
Claims from bb9_c7m12_1RB0RA_0RI0LC.md section 10.1 (D(m) = (10)^m 1):
  K(0^11; 0; b) -> Lambda(b) = 11 D4 D21 D4 D17 D4^(12b-12) D1 D34 (10)^44 111001  in 4356 b^2 + 13254 b + 28278 steps,
  head in B on the blank right of the word; then the champion rules R1-R3 run on the list (D17 acting as a digit).

  python verify_lambda.py rebuild [BMAX=4]      # the rebuild word, bit for bit, at the claimed step
  python verify_lambda.py chain B NCONF        # successive K-shaped configurations from Lambda(B), as D-token lists

Uses only ligocki_notation.Sim (plain literal simulator, BB(2)-BB(5) validated) and r4grid.tmpl_from; nothing from the
investigator's scripts.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'bb8_champ35_vs_bb7'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'rebuilder_nbrs'))
from ligocki_notation import Sim, parse_tm  # noqa: E402
from r4grid import tmpl_from  # noqa: E402

M11 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---'
M12 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RH0RE_0LH---'
TMPL = 'R,B,P=11,u=10,s=1,d=3d+1,b=3b+2,S=111001'


def D(m):
    return '10' * m + '1'


def lam(b):
    return '11' + D(4) + D(21) + D(4) + D(17) + D(4) * (12 * b - 12) + D(1) + D(34) + '10' * 44 + '111001'


def start_word(b):
    o, T = tmpl_from(TMPL)
    return T.build((0,) * 11, 0, b), T.q


def tokens(word):
    """'11' D(m1) ... D(mk) (10)^r '111001'  ->  ([m1..mk], r) or None."""
    m = re.fullmatch(r'11((?:(?:10)*1)*)((?:10)*)111001', word)
    if not m:
        return None
    ms = [len(t) // 2 for t in re.findall(r'((?:10)*)1', m.group(1))]
    return ms, len(m.group(2)) // 2


def tape_word(sim):
    """Word from the leftmost 1 up to the cell left of the head (head on a blank right of everything)."""
    s = sim.tape_str()
    return s


def rebuild(bmax):
    for name, m in (('#11', M11), ('#12', M12)):
        tm = parse_tm(m)
        for b in range(1, bmax + 1):
            w, q = start_word(b)
            steps = 4356 * b * b + 13254 * b + 28278
            sim = Sim(tm, w, head=len(w), state=q)
            sim.run(steps)
            got = sim.tape_str()
            head_ok = sim.state == q and sim.pos == sim.r1 + 1
            exp = lam(b)
            print(f'{name} b={b}: {steps} steps, state {chr(65 + sim.state)}, head right of the word: {head_ok}, '
                  f'word matches Lambda(b): {got == exp}  (len {len(got)} vs {len(exp)})')
            if got != exp:
                t = tokens(got)
                print('   got tokens:', t[0][:12] if t else None, '... r =', t[1] if t else None)


def chain(b, nconf):
    tm = parse_tm(M11)
    w = lam(b)
    o, T = tmpl_from(TMPL)
    sim = Sim(tm, w, head=len(w), state=T.q)
    seen = []

    def cb(step, s):
        t = tokens(s)
        if t is not None and step > 0:
            seen.append((step, t))
            if len(seen) >= nconf:
                raise StopIteration

    print('start:', tokens(w))
    try:
        sim.run(10 ** 9, T.q, cb)
    except StopIteration:
        pass
    for step, (ms, r) in seen:
        print(f'  step {step:>10}: tokens {ms}  acc-run r = {r}')


if __name__ == '__main__':
    if sys.argv[1] == 'rebuild':
        rebuild(int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    else:
        chain(int(sys.argv[2]), int(sys.argv[3]))
