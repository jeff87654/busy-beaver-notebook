"""Run-length TM simulator with chain (same-state run) acceleration.
Tape: L, R stacks of [sym,cnt] (top = nearest head); head sits between them facing 'R' (reads R top) or 'L'."""
import sys
from machines import parse

class Sim:
    def __init__(self, s):
        self.T = parse(s); self.L = []; self.R = []; self.face = 'R'; self.st = 'A'
        self.steps = 0; self.halted = False
    @staticmethod
    def push(stk, sym, n):
        if n <= 0: return
        if stk and stk[-1][0] == sym: stk[-1][1] += n
        elif not stk and sym == 0: return   # blank beyond end
        else: stk.append([sym, n])
    @staticmethod
    def pop1(stk):
        if not stk: return 0
        s = stk[-1][0]; stk[-1][1] -= 1
        if stk[-1][1] == 0: stk.pop()
        return s
    def step(self):
        src = self.R if self.face == 'R' else self.L
        dst = self.L if self.face == 'R' else self.R
        sym = src[-1][0] if src else 0
        tr = self.T[(self.st, sym)]
        if tr is None:
            self.halted = True; self.steps += 1; return
        w, d, ns = tr
        if d == self.face and ns == self.st:   # chain across the run
            if not src: raise RuntimeError('infinite chain into blank: non-halting')
            n = src.pop()[1]; self.push(dst, w, n); self.steps += n
        elif d == self.face:
            self.pop1(src); self.push(dst, w, 1); self.steps += 1
        else:
            self.pop1(src); self.push(src, w, 1); self.face = d; self.steps += 1
        self.st = ns
    def tape(self, maxruns=60):
        def fmt(runs):
            return ' '.join(f"{s}^{n}" if n > 1 else f"{s}" for s, n in runs)
        l = fmt(self.L); r = fmt(list(reversed(self.R)))
        head = f"<{self.st}" if self.face == 'L' else f"{self.st}>"
        return f"{l} {head} {r}"
