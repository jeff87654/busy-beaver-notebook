"""Reference semantics of a proof candidate, written directly over the bit string (no DAG, no SM
primitives): decode axiom codes / params with the prefix codes, apply the steps to the theorem
stack, CHECK after every complete step.  Used to cross-check the DAG program on the SM.

Bit conventions (must match sm_prog.py):
  axiom code: the prefix code dict (bit 1 = X branch);  variable: 1^i 0;
  wff token: e=0  ==10  ->=110  ~=1110  A=1111, then for e/= two variables, for A one variable.
"""
from sm_abstract import E, EQ, IM, NOT, ALL, V0, is_wff, CONTRADICTION, BOOT_THEOREM
import sm_prog


class End(Exception):
    pass


class Reader:
    def __init__(self, bits):
        self.bits = bits
        self.pos = 0

    def bit(self):
        if self.pos >= len(self.bits):
            raise End
        b = self.bits[self.pos]
        self.pos += 1
        return b

    def var(self):
        i = 0
        while self.bit() == 1:
            i += 1
        return V0 + i

    def wff(self):
        out = []
        pending = 1
        while pending:
            if self.bit() == 0:
                t = E
            elif self.bit() == 0:
                t = EQ
            elif self.bit() == 0:
                t = IM
            elif self.bit() == 0:
                t = NOT
            else:
                t = ALL
            out.append(t)
            if t in (E, EQ):
                out.append(self.var()); out.append(self.var())
                pending -= 1
            elif t == IM:
                pending += 1
            elif t == ALL:
                out.append(self.var())
        return tuple(out)

    def code(self, code):
        inv = {w: a for a, w in code.items()}
        w = ''
        while w not in inv:
            w += str(self.bit())
        return inv[w]


def _trie(code, gen_style):
    return sm_prog.trie(code, gen_style if gen_style else sm_prog.DEFAULT_GEN, sm_prog.DEFAULT_FACTOR)


def decode(bits, code, gen_style=None):
    """-> (list of complete steps (name, params tuple), number of bits consumed by them).
    The order of code bits and param reads follows the dispatch trie (params shared by a group
    of axioms are read before the bits that separate the group)."""
    r = Reader(bits)
    root = _trie(code, gen_style)
    steps = []
    used = 0
    try:
        while True:
            node = root
            reads = []
            while True:
                pre = node[2] if node[0] == 'leaf' else node[1]
                for x in pre:
                    if x in ('RV', 'VAR'):
                        reads.append((r.var(),))
                    elif x == 'RW':
                        reads.append(r.wff())
                if node[0] == 'leaf':
                    break
                node = node[2] if r.bit() == 1 else node[3]
            a = node[1]
            if a == 'GEN':
                assert len(reads) == 1
            else:
                assert len(reads) == len(sm_prog.param_kinds(a)), (a, reads)
            steps.append((a, tuple(reads)))
            used = r.pos
    except End:
        pass
    return steps, used


def apply(A, step, check_target=CONTRADICTION):
    """Apply one step to the stack A (list, modified); return True iff CHECK halts after it."""
    a, ps = step
    if a == 'DET':
        if len(A) >= 2:
            X, Y = A[-1], A[-2]
            if X[0] == IM:
                if X[1:1 + len(Y)] == Y:
                    A.pop(); A.pop(); A.append(X[1 + len(Y):])
                else:
                    A.pop()
    elif a == 'GEN':
        A.append((ALL,) + ps[0] + A[-1])
    else:
        names = sm_prog.AXDICT[a][1].split()
        A.append(sm_prog.instantiate(a, dict(zip(names, ps))))
    assert is_wff(A[-1])
    return bool(A) and A[-1] == tuple(check_target)


def run(A, bits, code, check_target=CONTRADICTION):
    """Run one candidate on stack A (modified).  Returns ('HALT'|'END', steps executed)."""
    steps, _ = decode(bits, code)
    for i, s in enumerate(steps):
        if apply(A, s, check_target):
            return 'HALT', i + 1
    return 'END', len(steps)


def encode(steps, code, gen_style=None):
    """Inverse of decode: steps = [(name, params)] with params as token tuples -> bit list."""
    bits = []
    root = _trie(code, gen_style)

    def var(t):
        assert len(t) == 1 and t[0] >= V0
        bits.extend([1] * (t[0] - V0) + [0])

    def wff(t):
        assert is_wff(t)
        i = 0
        while i < len(t):
            x = t[i]
            bits.extend({E: [0], EQ: [1, 0], IM: [1, 1, 0], NOT: [1, 1, 1, 0], ALL: [1, 1, 1, 1]}[x])
            i += 1
            if x in (E, EQ):
                var(t[i:i + 1]); var(t[i + 1:i + 2]); i += 2
            elif x == ALL:
                var(t[i:i + 1]); i += 1

    for a, ps in steps:
        w = code[a]
        ps = list(ps)
        node = root
        d = 0
        while True:
            pre = node[2] if node[0] == 'leaf' else node[1]
            for x in pre:
                if x in ('RV', 'VAR'):
                    var(ps.pop(0))
                elif x == 'RW':
                    wff(ps.pop(0))
            if node[0] == 'leaf':
                break
            b = int(w[d]); d += 1
            bits.append(b)
            node = node[2] if b == 1 else node[3]
        assert node[1] == a and not ps
    return bits
