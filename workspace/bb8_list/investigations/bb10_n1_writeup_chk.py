"""Independent literal checks for bb10_n1_writeup.md (own simulator; B-form = 0^inf D(t1)..D(tn) D0 D(A) H> 0^inf).
   Run at Idle priority, e.g. python -c "import subprocess,sys; subprocess.run([sys.executable,'bb10_n1_writeup_chk.py'], creationflags=0x40)"
   (about 10 s). Checks: start-up landmarks (steps 6447, 48159), R1, R2, H, S0, P1-P4, E (both size orders for the
   unpacks P2/P4/E) and HALT with its exact ones count."""
import re, sys, random

M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
TR = {}
for i, row in enumerate(M.split('_')):
    q = 'ABCDEFGHIJ'[i]
    for s in (0, 1):
        t = row[3 * s:3 * s + 3]
        TR[(q, s)] = None if t == '---' else (int(t[0]), 1 if t[1] == 'R' else -1, t[2])


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
    def __init__(self, word, head, state):
        self.pad = 64
        self.t = bytearray(self.pad) + bytearray(int(c) for c in word) + bytearray(self.pad)
        self.h = self.pad + head
        self.q = state
        self.steps = 0

    def step(self):
        tr = TR[(self.q, self.t[self.h])]
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

    def word(self):
        s = ''.join('1' if b else '0' for b in self.t)
        i = s.find('1')
        return s, i

    def bform(self):
        """B-form test: state H, head on a 0 right of the last 1, the 1 immediately left; returns (prefix_items, L, A)."""
        if self.q != 'H' or self.t[self.h] != 0 or self.t[self.h - 1] != 1:
            return None
        if any(self.t[self.h:]):
            return None
        s = ''.join('1' if b else '0' for b in self.t[:self.h])
        i = s.find('1')
        it = toks(s[i:])
        # active list: tokens after the last zero run
        j = len(it)
        while j > 0 and isinstance(it[j - 1], int):
            j -= 1
        act = it[j:]
        if len(act) < 2 or act[-2] != 0:
            return None
        return it[:j], act[:-2], act[-1]

    def ones(self):
        return sum(self.t)


def run_to_b(word, head, state, maxsteps=10 ** 8, skip_first=True):
    T = Tape(word, head, state)
    while T.steps < maxsteps:
        if not T.step():
            return 'HALT', T
        r = T.bform()
        if r is not None:
            return 'B', (T, r)
    return 'TIME', T


def from_b(L, A, far=''):
    w = bword(L, A, far)
    return run_to_b(w, len(w), 'H')


def far_items(far):
    return toks(far.lstrip('0')) if far else []


def check(name, L, A, expL, expA, far='', expfar=None):
    kind, res = from_b(L, A, far)
    if kind != 'B':
        return False, kind
    T, (pre, L2, A2) = res
    ok = (L2 == expL and A2 == expA)
    if expfar is not None:
        ok = ok and pre == far_items(expfar)
    elif far == '':
        ok = ok and pre == []
    return ok, T.steps


FARP = lambda k, m: bword([2] * (k + 2) + [5] + [1] * m + [0, 0], 0)[:-1] + '00'  # D2^(k+2) D5 D1^m D0 D0 D0 00
TAIL = '10110101010101010010000010111100100100100100'
FARE = lambda k: '10101' * k + TAIL

if __name__ == '__main__':
    out = []
    # 1. start-up from blank
    T = Tape('0', 0, 'A')
    marks = {}
    while T.steps < 48159:
        T.step()
        if T.steps in (6447, 48159):
            marks[T.steps] = T.bform()
    print('startup', {k: (v[0], v[1][:3], len(v[1]), v[2]) if v else None for k, v in marks.items()})
    print('  6447 list == [7]+[1]*35:', marks[6447] and marks[6447][1] == [7] + [1] * 35 and marks[6447][2] == 4)
    print('  48159 list == [4]*36, A=16:', marks[48159] and marks[48159][1] == [4] * 36 and marks[48159][2] == 16)
    rng = random.Random(1)
    res = {}

    def tally(nm, ok):
        a = res.setdefault(nm, [0, 0])
        a[0 if ok else 1] += 1

    for _ in range(12):
        Ls = [rng.choice([1, 4, 7]) for _ in range(rng.randint(0, 3))]
        t = rng.randint(0, 9); A = rng.randint(0, 40)
        ok, st = check('R1', Ls + [t + 3], A, Ls + [t], 2 * A + 8); tally('R1', ok)
        k = rng.randint(0, 6)
        ok, st = check('R2', Ls + [t + 3] + [1] * (k + 1), A, Ls + [t, A + 3] + [1] * k, 4); tally('R2', ok)
    for n in range(0, 6):
        for a in (4, 6, 7, 10, 13):
            ok, st = check('H', [1] * (n + 1), a, [2] + [1] * (2 * a + 4) + [0] + [1] * n, 6); tally('H', ok)
    for M_ in (0, 3, 7, 12, 30):
        for n in (0, 1, 4):
            for a in (4, 6, 9):
                ok, st = check('S0', [2] + [1] * (M_ + 5) + [0] + [1] * (n + 2), a,
                               [2, 5] + [1] * M_ + [0, 0, 0, a + 3] + [1] * n, 4); tally('S0', ok)
    for _ in range(15):
        k, m, n, a = rng.randint(0, 8), rng.randint(0, 20), rng.randint(0, 12), 3 * rng.randint(0, 60) + 1
        ok, st = check('P1', [2] * k + [5] + [1] * (m + 6) + [0, 0, 2] + [1] * n, a,
                       [2] * (k + 2) + [5] + [1] * m + [0, 0, 0, 1, a + 3] + [1] * n, 6); tally('P1', ok)
    # P2 both size orders: p >> r and r >> p
    for p, r in [(13, 0), (13, 3), (400, 3), (3, 300), (1, 999), (1000, 2), (0, 0), (50, 50)]:
        for k, m, w in [(0, 0, 0), (2, 5, 3), (5, 11, 9)]:
            ok, st = check('P2', [2] * k + [5] + [1] * (m + 6) + [0, 0, 0, 1, 1 + 3 * p, 0] + [1] * (w + 1), r + 1,
                           [2, r + 2] + [1] * (w + 2 * p + 2), 4, expfar=FARP(k, m)); tally('P2', ok)
    for _ in range(12):
        k, m, w, a = rng.randint(0, 8), rng.randint(0, 20), rng.randint(0, 12), rng.randint(0, 300)
        ok, st = check('P3', [2, 2] + [1] * w, a, [2] * (k + 2) + [5] + [1] * m + [0, 0, a + 5] + [1] * w, 6,
                       far=FARP(k, m)); tally('P3', ok)
    for q, r in [(0, 0), (14, 2), (400, 2), (1, 900), (2, 2000), (300, 300)]:
        for k, m, w in [(0, 0, 0), (3, 4, 2), (7, 13, 10)]:
            ok, st = check('P4', [2] * k + [5] + [1] * (m + 2) + [0, 0, 3 * q, 0] + [1] * (w + 1), r + 1,
                           [2] * k + [5] + [1] * m + [0, 0, r + 2] + [1] * (w + 2 * q + 2), 4); tally('P4', ok)
    for p, r in [(13, 0), (400, 3), (2, 500), (0, 0)]:
        for k, w in [(0, 0), (3, 4), (11, 20)]:
            ok, st = check('E', [2] * (k + 6) + [5, 1, 0, 0, 0, 1, 1 + 3 * p, 0] + [1] * (w + 1), r + 1,
                           [r + 3] + [1] * (w + 2 * p + 2), 4, expfar=FARE(k)); tally('E', ok)
    hs = []
    for k in (0, 1, 5, 17):
        for w in (0, 1, 2, 7, 30):
            for f in (0, 1, 4, 40, 301):
                wd = bword([0] + [1] * w, f, FARE(k))
                T = Tape(wd, len(wd), 'H')
                while T.step():
                    if T.steps > 10 ** 7:
                        break
                ok = (T.q == 'J' and T.t[T.h] == 0 and T.ones() == 2 * w + f + 3 * k + 22)
                tally('HALT', ok)
                hs.append(T.steps)
    print('HALT steps min/max', min(hs), max(hs))
    for nm, (a, b) in res.items():
        print('%-5s %d ok %d bad' % (nm, a, b))
