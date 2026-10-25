"""Block-3 macro simulator with chain steps (exact; like Ligocki's macro machine without backsymbols/prover).
Tape = left stack + right stack of [block, count], nearest-to-head LAST.  Head sits between the stacks, in
state q, facing direction d ('R': about to enter right stack's top block at its left edge; 'L' symmetric).
"""
ST = "ABCDEFGH"
Z = (0, 0, 0)

def parse(tm):
    t = {}
    for qi, ch in enumerate(tm.split('_')):
        for s in (0, 1):
            e = ch[3*s:3*s+3]
            t[(ST[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, e[2])
    return t

class Halt(Exception):
    pass

class MSim:
    def __init__(self, tm, B=3):
        self.T = parse(tm)
        self.B = B
        self.cache = {}
        self.L = []; self.R = []
        self.q = 'A'; self.d = 'R'
        self.steps = 0
        self.Z = (0,) * B

    def trans(self, q, blk, d):
        key = (q, blk, d)
        if key in self.cache:
            return self.cache[key]
        b = list(blk)
        pos = 0 if d == 'R' else self.B - 1
        n = 0
        seen = set()
        while 0 <= pos < self.B:
            st = (q, pos, tuple(b))
            if st in seen:
                self.cache[key] = 'LOOP'; return 'LOOP'
            seen.add(st)
            tr = self.T[(q, b[pos])]
            if tr is None:
                res = ('HALT', q, pos, tuple(b), n)
                self.cache[key] = res
                return res
            w, mv, q = tr
            b[pos] = w; pos += mv; n += 1
        res = (tuple(b), q, 'R' if pos >= self.B else 'L', n)
        self.cache[key] = res
        return res

    @staticmethod
    def push(stk, blk, cnt):
        if cnt == 0: return
        if stk and stk[-1][0] == blk:
            stk[-1][1] += cnt
        else:
            stk.append([blk, cnt])

    def step(self):
        facing = self.R if self.d == 'R' else self.L
        other = self.L if self.d == 'R' else self.R
        if facing:
            blk, cnt = facing[-1]
        else:
            blk, cnt = self.Z, None
        res = self.trans(self.q, blk, self.d)
        if res == 'LOOP':
            raise Halt('LOOP')
        if res[0] == 'HALT':
            raise Halt(res)
        nb, q2, d2, n = res
        if d2 == self.d and q2 == self.q and cnt is not None:
            # chain over the whole run
            facing.pop()
            self.push(other, nb, cnt)
            self.steps += n * cnt
            return
        if cnt is not None:
            if cnt == 1: facing.pop()
            else: facing[-1][1] -= 1
        if d2 == self.d:
            self.push(other, nb, 1)
        else:
            if nb != self.Z or facing:
                self.push(facing, nb, 1)
        self.q, self.d = q2, d2
        self.steps += n

    def show(self, big=12):
        def e(c):
            s = str(c)
            return s if len(s) <= big else '~1e%d' % (len(s) - 1)
        ls = ' '.join('%s^%s' % (''.join(map(str, b)), e(c)) for b, c in self.L)
        rs = ' '.join('%s^%s' % (''.join(map(str, b)), e(c)) for b, c in reversed(self.R))
        if self.d == 'R':
            return '%s %s> %s' % (ls, self.q, rs)
        return '%s <%s %s' % (ls, self.q, rs)

def from_blocks(tm, left, q, d, right, B=3):
    """left/right: lists of (blockstring, count) in LEFT-TO-RIGHT tape order."""
    s = MSim(tm, B)
    for b, c in left:
        MSim.push(s.L, tuple(int(ch) for ch in b), c)
    for b, c in reversed(right):
        MSim.push(s.R, tuple(int(ch) for ch in b), c)
    s.q, s.d = q, d
    return s
