"""Lazy-branching search over ALL (E0, I0, I1, J0, J1) gadgets on the GH base to find all gadgets that:
1) reproduce S0, P1, P2, P4, E and halt at HALT (comparing their HALT ones count against n1), OR
2) produce a modified B-form on S0 / P1 / P2 / P4 / E!"""
import re

BASE_GH = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_0RG1LD_1RH1LG_1LC0RG_------_------'

def D(m):
    return '10' * m + '1'

def bword(L, A, far=''):
    return far + ''.join(D(t) for t in L) + D(0) + D(A)

TOKRE = re.compile(r'(?:10)*1|0+')
def toks(word):
    out = []
    for g in TOKRE.findall(word):
        out.append(('z%d' % len(g)) if g[0] == '0' else (len(g) - 1) // 2)
    return out

BASE_TR = {}
for i, row in enumerate(BASE_GH.split('_')[:8]):
    q = 'ABCDEFGH'[i]
    for s in (0, 1):
        t = row[3 * s:3 * s + 3]
        BASE_TR[(q, s)] = None if t == '---' else (int(t[0]), 1 if t[1] == 'R' else -1, t[2])
del BASE_TR[('E', 0)]

OPTS_E0 = [(w, d, 'I') for w in (0, 1) for d in (-1, 1)]
OPTS_IJ = [(w, d, q) for w in (0, 1) for d in (-1, 1) for q in 'ABCDEFGHIJ']

FARP = lambda k, m: bword([2] * (k + 2) + [5] + [1] * m + [0, 0], 0)[:-1] + '00'
TAIL = '10110101010101010010000010111100100100100100'
FARE = lambda k: '10101' * k + TAIL

def run_lazy(tr, word, want_halt=False, maxsteps=1500):
    pad = 32
    t = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
    h = pad + len(word)
    q = 'H'
    steps = 0
    while steps < maxsteps:
        key = (q, t[h])
        if key not in tr:
            return 'BRANCH', key
        val = tr[key]
        if val is None:
            return 'HALT', (q, t[h], sum(t), steps)
        w, d, q = val
        t[h] = w
        h += d
        if h < 2:
            t = bytearray(pad) + t
            h += pad
        elif h >= len(t) - 2:
            t += bytearray(pad)
        steps += 1
        if not want_halt and q == 'H' and t[h] == 0 and t[h - 1] == 1 and not any(t[h:]):
            s = ''.join('1' if b else '0' for b in t[:h])
            i = s.find('1')
            it = toks(s[i:])
            j = len(it)
            while j > 0 and isinstance(it[j - 1], int):
                j -= 1
            act = it[j:]
            if len(act) >= 2 and act[-2] == 0:
                return 'B', (it[:j], act[:-2], act[-1], steps)
    return 'TIME', None

def fmt_tr(tr):
    def f(key):
        v = tr.get(key)
        if v is None:
            return '---'
        w, d, q = v
        return f"{w}{'R' if d == 1 else 'L'}{q}"
    return f"E0={f(('E',0))} I={f(('I',0))}{f(('I',1))} J={f(('J',0))}{f(('J',1))}"

def main():
    TR_N1 = dict(BASE_TR)
    TR_N1[('E', 0)] = (1, -1, 'I')
    TR_N1[('I', 0)] = (0, -1, 'J')
    TR_N1[('I', 1)] = (0, -1, 'I')
    TR_N1[('J', 0)] = None
    TR_N1[('J', 1)] = (0, -1, 'C')

    # Full macro tests S0, P1, P2, P4, E computed directly from TR_N1:
    w_s0 = bword([2] + [1]*8 + [0, 1, 1, 1], 6)
    w_p1 = bword([2, 5] + [1]*7 + [0, 0, 2, 1, 1], 7)
    w_p2 = bword([2, 5] + [1]*7 + [0, 0, 0, 1, 4, 0, 1, 1], 4)
    w_p4 = bword([2, 5] + [1]*3 + [0, 0, 3, 0, 1, 1], 4)
    w_e  = bword([2]*7 + [5, 1, 0, 0, 0, 1, 4, 0, 1, 1], 4)

    tests = []
    for tname, wd in [('S0', w_s0), ('P1', w_p1), ('P2', w_p2), ('P4', w_p4), ('E', w_e)]:
        k_, r_ = run_lazy(TR_N1, wd, want_halt=False, maxsteps=2000)
        assert k_ == 'B', (tname, k_, r_)
        tests.append((tname, wd, r_[:3], r_[3] + 200))

    w_halt = bword([0, 1, 1], 4, FARE(1))
    _, (_, _, n1_halt_ones, n1_halt_steps) = run_lazy(TR_N1, w_halt, want_halt=True, maxsteps=2000)
    print(f"n1 HALT baseline: ones={n1_halt_ones}, steps={n1_halt_steps}")

    exact_matches = []
    alt_s0_bforms = []

    def dfs(tr, stage_idx):
        if stage_idx < len(tests):
            tname, wd, exp, msteps = tests[stage_idx]
            kind, res = run_lazy(tr, wd, want_halt=False, maxsteps=msteps)
            if kind == 'BRANCH':
                key = res
                used_ij = sum(1 for q in ('I', 'J') for b in (0, 1) if (q, b) in tr)
                if key != ('E', 0) and used_ij >= 3:
                    return
                opts = OPTS_E0 if key == ('E', 0) else OPTS_IJ
                for o in opts:
                    tr2 = dict(tr)
                    tr2[key] = o
                    dfs(tr2, stage_idx)
                return
            if kind == 'B':
                if res[:3] == exp:
                    dfs(tr, stage_idx + 1)
                elif stage_idx == 0:
                    alt_s0_bforms.append((dict(tr), res))
            return
        # Passed S0, P1, P2, P4, E! Now test HALT:
        kind, res = run_lazy(tr, w_halt, want_halt=True, maxsteps=2000)
        if kind == 'BRANCH':
            key = res
            #Can either halt right here (None) or take a transition!
            tr_halt = dict(tr)
            tr_halt[key] = None
            dfs(tr_halt, stage_idx)
            # Only branch further if there is still at least one unused IJ slot left for ---
            used_ij = sum(1 for q in ('I', 'J') for b in (0, 1) if (q, b) in tr)
            if used_ij < 3:
                for o in OPTS_IJ:
                    tr2 = dict(tr)
                    tr2[key] = o
                    dfs(tr2, stage_idx)
            return
        if kind == 'HALT':
            # Check that at least one IJ slot is None or unused
            exact_matches.append((dict(tr), res))

    dfs(dict(BASE_TR), 0)
    print(f"Found {len(exact_matches)} gadgets matching S0, P1, P2, P4, E and halting on HALT:")
    for tr, (hq, hb, ones, steps) in sorted(exact_matches, key=lambda x: -x[1][2]):
        diff = ones - n1_halt_ones
        print(f"  {fmt_tr(tr):32s} -> HALT at {hq}{hb}, steps={steps:5d}, ones={ones} (diff vs n1: {diff:+d})")

    print(f"\nFound {len(alt_s0_bforms)} gadgets producing alternative B-forms on S0.")
    # Group alt_s0_bforms by output shape
    by_shape = {}
    for tr, (pre, L2, A2, st) in alt_s0_bforms:
        by_shape.setdefault((tuple(pre), tuple(L2), A2), []).append(tr)
    print(f"Distinct alternative S0 B-forms: {len(by_shape)}")
    for (pre, L2, A2), trs in sorted(by_shape.items(), key=lambda x: -len(x[1]))[:25]:
        print(f"  count={len(trs):4d} | pre={list(pre)} L={list(L2)} A={A2} | ex: {fmt_tr(trs[0])}")

if __name__ == '__main__':
    main()
