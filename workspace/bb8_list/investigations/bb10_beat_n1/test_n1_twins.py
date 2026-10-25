"""Fast test of n1 and its gadget/base variants on all literal rules of BB10_n1.v."""
import re, random

MACHINES = {
    'n1_GH_0LJ0LI_---0LC':  ('1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC', 'H'),
    'n1_GH_---0LJ_0LE0LJ':  ('1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LJ_0LE0LJ', 'H'),
    'n1_REC_0LJ0LI_---0LC': ('1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_0LJ0LI_---0LC', 'G'),
    'n1_REC_---0LJ_0LE0LJ': ('1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LE0LJ', 'G'),
    'n1_H_0LJ0LI_---0LC':   ('1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LH_0LJ0LI_---0LC', 'G'),
    'n1_H_---0LJ_0LE0LJ':   ('1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LH_---0LJ_0LE0LJ', 'G'),
}

def parse_tm(m):
    tr = {}
    for i, row in enumerate(m.split('_')):
        q = 'ABCDEFGHIJ'[i]
        for s in (0, 1):
            t = row[3 * s:3 * s + 3]
            tr[(q, s)] = None if t == '---' else (int(t[0]), 1 if t[1] == 'R' else -1, t[2])
    return tr

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

class Tape:
    def __init__(self, tr, word, head, state, canon_state='H'):
        self.tr = tr
        self.canon_state = canon_state
        self.pad = 64
        self.t = bytearray(self.pad) + bytearray(int(c) for c in word) + bytearray(self.pad)
        self.h = self.pad + head
        self.q = state
        self.steps = 0

    def step(self):
        tr = self.tr[(self.q, self.t[self.h])]
        if tr is None:
            return False
        w, d, q = tr
        self.t[self.h] = w
        self.h += d
        self.q = q
        if self.h < 2:
            self.t = bytearray(self.pad) + self.t
            self.h += self.pad
        elif self.h >= len(self.t) - 2:
            self.t += bytearray(self.pad)
        self.steps += 1
        return True

    def bform(self):
        if self.q != self.canon_state or self.t[self.h] != 0 or self.t[self.h - 1] != 1:
            return None
        if any(self.t[self.h:]):
            return None
        s = ''.join('1' if b else '0' for b in self.t[:self.h])
        i = s.find('1')
        it = toks(s[i:])
        j = len(it)
        while j > 0 and isinstance(it[j - 1], int):
            j -= 1
        act = it[j:]
        if len(act) < 2 or act[-2] != 0:
            return None
        return it[:j], act[:-2], act[-1]

    def ones(self):
        return sum(self.t)

def run_to_b(tr, word, head, state, canon_state='H', maxsteps=500000):
    T = Tape(tr, word, head, state, canon_state)
    cs = canon_state
    while T.steps < maxsteps:
        if not T.step():
            return 'HALT', T
        if T.q == cs and T.t[T.h] == 0 and T.t[T.h - 1] == 1:
            r = T.bform()
            if r is not None:
                return 'B', (T, r)
    return 'TIME', T

def from_b(tr, L, A, far='', canon_state='H'):
    w = bword(L, A, far)
    return run_to_b(tr, w, len(w), canon_state, canon_state)

def far_items(far):
    return toks(far.lstrip('0')) if far else []

FARP = lambda k, m: bword([2] * (k + 2) + [5] + [1] * m + [0, 0], 0)[:-1] + '00'
TAIL = '10110101010101010010000010111100100100100100'
FARE = lambda k: '10101' * k + TAIL

def test_machine(name, m, canon_state):
    tr = parse_tm(m)
    print(f"=== {name}: {m} (canon={canon_state}) ===", flush=True)
    T = Tape(tr, '0', 0, 'A', canon_state)
    bforms = []
    while T.steps < 50000:
        T.step()
        if T.q == canon_state and T.t[T.h] == 0 and T.t[T.h - 1] == 1:
            bf = T.bform()
            if bf and bf[1] == [7] + [1]*35 and bf[2] == 4:
                bforms.append(('start35', T.steps))
            if bf and bf[1] == [4]*36 and bf[2] == 16:
                bforms.append(('all4_36', T.steps))
    print("  Landmarks:", bforms, flush=True)

    rng = random.Random(1)
    res = {}
    def tally(nm, ok):
        a = res.setdefault(nm, [0, 0])
        a[0 if ok else 1] += 1

    def check(L, A, expL, expA, far='', expfar=None):
        kind, r = from_b(tr, L, A, far, canon_state)
        if kind != 'B':
            return False
        T_, (pre, L2, A2) = r
        ok = (L2 == expL and A2 == expA)
        if expfar is not None:
            ok = ok and pre == far_items(expfar)
        elif far == '':
            ok = ok and pre == []
        return ok

    for _ in range(6):
        Ls = [rng.choice([1, 4, 7]) for _ in range(rng.randint(0, 2))]
        t = rng.randint(0, 6); A = rng.randint(0, 20)
        tally('R1', check(Ls + [t + 3], A, Ls + [t], 2 * A + 8))
        k = rng.randint(0, 4)
        tally('R2', check(Ls + [t + 3] + [1] * (k + 1), A, Ls + [t, A + 3] + [1] * k, 4))
    for n in range(0, 3):
        for a in (4, 6, 7):
            tally('H', check([1] * (n + 1), a, [2] + [1] * (2 * a + 4) + [0] + [1] * n, 6))
    for M_ in (0, 3, 7):
        for n in (0, 1, 4):
            for a in (4, 6, 9):
                tally('S0', check([2] + [1] * (M_ + 5) + [0] + [1] * (n + 2), a,
                                  [2, 5] + [1] * M_ + [0, 0, 0, a + 3] + [1] * n, 4))
    for _ in range(6):
        k, m_, n, a = rng.randint(0, 4), rng.randint(0, 10), rng.randint(0, 5), 3 * rng.randint(0, 20) + 1
        tally('P1', check([2] * k + [5] + [1] * (m_ + 6) + [0, 0, 2] + [1] * n, a,
                          [2] * (k + 2) + [5] + [1] * m_ + [0, 0, 0, 1, a + 3] + [1] * n, 6))
    for p, r in [(13, 0), (13, 3), (40, 3), (3, 40), (0, 0)]:
        for k, m_, w in [(0, 0, 0), (2, 5, 3)]:
            tally('P2', check([2] * k + [5] + [1] * (m_ + 6) + [0, 0, 0, 1, 1 + 3 * p, 0] + [1] * (w + 1), r + 1,
                              [2, r + 2] + [1] * (w + 2 * p + 2), 4, expfar=FARP(k, m_)))
    for _ in range(6):
        k, m_, w, a = rng.randint(0, 4), rng.randint(0, 10), rng.randint(0, 5), rng.randint(0, 40)
        tally('P3', check([2, 2] + [1] * w, a, [2] * (k + 2) + [5] + [1] * m_ + [0, 0, a + 5] + [1] * w, 6,
                          far=FARP(k, m_)))
    for q, r in [(0, 0), (14, 2), (40, 2), (1, 40)]:
        for k, m_, w in [(0, 0, 0), (3, 4, 2)]:
            tally('P4', check([2] * k + [5] + [1] * (m_ + 2) + [0, 0, 3 * q, 0] + [1] * (w + 1), r + 1,
                              [2] * k + [5] + [1] * m_ + [0, 0, r + 2] + [1] * (w + 2 * q + 2), 4))
    for p, r in [(13, 0), (40, 3), (2, 40), (0, 0)]:
        for k, w in [(0, 0), (3, 4)]:
            tally('E', check([2] * (k + 6) + [5, 1, 0, 0, 0, 1, 1 + 3 * p, 0] + [1] * (w + 1), r + 1,
                             [r + 3] + [1] * (w + 2 * p + 2), 4, expfar=FARE(k)))
    halt_diffs = set()
    for k in (0, 1, 5):
        for w in (0, 1, 2, 7):
            for f in (0, 1, 4, 40):
                wd = bword([0] + [1] * w, f, FARE(k))
                T_ = Tape(tr, wd, len(wd), canon_state, canon_state)
                while T_.step():
                    if T_.steps > 200000:
                        break
                exp_n1 = 2 * w + f + 3 * k + 22
                diff = T_.ones() - exp_n1
                halt_diffs.add((T_.q, T_.t[T_.h], diff))
                tally('HALT', T_.steps <= 200000)
    print("  Results:", res, flush=True)
    print("  HALT (state, bit, ones - ones_n1):", halt_diffs, flush=True)

if __name__ == '__main__':
    for nm, (m, cs) in MACHINES.items():
        test_machine(nm, m, cs)
