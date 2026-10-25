"""Profile transition usage and E0 entry contexts across all phases of n1, and find all (E0, I0, I1, J0, J1) gadgets that preserve S0, P1..P4, E and halt at HALT."""
import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb10_n1_coq')
import planner8 as pl
import engine, coqgen, mexp
from evs import EV
from gen_base import RULES as BASE

M_N1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
M_P1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LJ_0LE0LJ'

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

class ProfTape:
    def __init__(self, tr, word, head, state, canon_state='H'):
        self.tr = tr
        self.canon_state = canon_state
        self.pad = 64
        self.t = bytearray(self.pad) + bytearray(int(c) for c in word) + bytearray(self.pad)
        self.h = self.pad + head
        self.q = state
        self.steps = 0
        self.usage = {}
        self.e0_ctxs = []

    def step(self):
        b = self.t[self.h]
        key = f"{self.q}{b}"
        self.usage[key] = self.usage.get(key, 0) + 1
        if key == 'E0':
            # record how many 1s are immediately left of h, and the 4 bits left of that
            k = 0
            p = self.h - 1
            while p >= 0 and self.t[p] == 1:
                k += 1
                p -= 1
            left4 = ''.join(str(self.t[i]) for i in range(max(0, p-3), p+1))
            right3 = ''.join(str(self.t[i]) for i in range(self.h, min(len(self.t), self.h+4)))
            self.e0_ctxs.append((left4, f"1^{k}", right3))
        tr = self.tr[(self.q, b)]
        if tr is None:
            return False
        w, d, q = tr
        self.t[self.h] = w
        self.h += d
        self.q = q
        if self.h < 8:
            self.t = bytearray(self.pad) + self.t
            self.h += self.pad
        elif self.h >= len(self.t) - 8:
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

def run_phase(tr, word, head, state, stop_steps=None):
    T = ProfTape(tr, word, head, state, 'H')
    while True:
        if not T.step():
            break
        if stop_steps and T.steps >= stop_steps:
            break
        if not stop_steps and T.q == 'H' and T.t[T.h] == 0 and T.t[T.h - 1] == 1:
            if T.bform() is not None:
                break
    return T

FARP = lambda k, m: bword([2] * (k + 2) + [5] + [1] * m + [0, 0], 0)[:-1] + '00'
TAIL = '10110101010101010010000010111100100100100100'
FARE = lambda k: '10101' * k + TAIL

def profile_machine(name, m):
    tr = parse_tm(m)
    print(f"=== Transition Profile for {name}: {m} ===")
    phases = [
        ('startup_6447', '0', 0, 'A', 6447),
        ('R1', bword([1, 5], 10), None, 'H', None),
        ('R2', bword([5, 1, 1], 10), None, 'H', None),
        ('H', bword([1, 1, 1], 7), None, 'H', None),
        ('S0', bword([2] + [1]*8 + [0, 1, 1, 1], 6), None, 'H', None),
        ('P1', bword([2, 2, 5] + [1]*8 + [0, 0, 2, 1, 1], 7), None, 'H', None),
        ('P2', bword([2, 2, 5] + [1]*8 + [0, 0, 0, 1, 7, 0, 1, 1], 4), None, 'H', None),
        ('P3', bword([2, 2, 1, 1], 7, FARP(2, 3)), None, 'H', None),
        ('P4', bword([2, 2, 5] + [1]*4 + [0, 0, 6, 0, 1, 1], 4), None, 'H', None),
        ('E', bword([2]*7 + [5, 1, 0, 0, 0, 1, 7, 0, 1, 1], 4), None, 'H', None),
        ('HALT', bword([0, 1, 1], 4, FARE(1)), None, 'H', None),
    ]
    all_slots = [f"{q}{b}" for q in 'ABCDEFGHIJ' for b in (0, 1)]
    total_u = {k: 0 for k in all_slots}
    for pname, wd, hd, st, ssteps in phases:
        if hd is None:
            hd = len(wd)
        T = run_phase(tr, wd, hd, st, ssteps)
        for k, v in T.usage.items():
            total_u[k] += v
        used_ij = {k: T.usage[k] for k in ['E0', 'E1', 'I0', 'I1', 'J0', 'J1'] if k in T.usage}
        ctxs = sorted(set(T.e0_ctxs))
        print(f"  {pname:12s}: steps={T.steps:6d} | E/I/J={used_ij} | E0_ctxs={ctxs}")
    unused = [k for k, v in total_u.items() if v == 0]
    print(f"  Total unused slots across entire run: {unused}")
    # Also check which slots are used ONLY in startup vs after startup
    startup_T = run_phase(tr, '0', 0, 'A', 6447)
    post_u = {k: total_u[k] - startup_T.usage.get(k, 0) for k in all_slots}
    only_startup = [k for k in all_slots if startup_T.usage.get(k, 0) > 0 and post_u[k] == 0]
    only_post = [k for k in all_slots if startup_T.usage.get(k, 0) == 0 and post_u[k] > 0]
    print(f"  Used ONLY in startup: {only_startup}")
    print(f"  Used ONLY post-startup: {only_post}\n")

if __name__ == '__main__':
    profile_machine('n1', M_N1)
    profile_machine('n1_plus1', M_P1)
