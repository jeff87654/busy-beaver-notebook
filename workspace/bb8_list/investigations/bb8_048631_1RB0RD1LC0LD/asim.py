"""msim + heuristic diff-rule acceleration (exploration only; NOT a proof tool).
When the tape signature (state, dir, block sequence without counts) recurs 3 times with the same count delta,
the cycle is extrapolated as long as every decreasing count stays above a safety margin."""
from msim import MSim, Halt, from_blocks

class ASim:
    def __init__(self, m, margin=4):
        self.m = m
        self.hist = {}
        self.margin = margin
        self.accel = 0
        self.nmacro = 0

    def sig(self):
        m = self.m
        return (m.q, m.d, tuple(b for b, c in m.L), tuple(b for b, c in m.R))

    def counts(self):
        m = self.m
        return [c for b, c in m.L] + [c for b, c in m.R]

    def step(self):
        m = self.m
        s = self.sig()
        v = self.counts()
        h = self.hist.get(s)
        if h is not None:
            (t0, v0, st0, d0) = h
            delta = [a - b for a, b in zip(v, v0)]
            dsteps = m.steps - st0
            if d0 is not None and d0[0] == delta and any(delta) and self.nmacro - t0 < 20000:
                # extrapolate k more cycles
                ks = []
                for c, dd in zip(v, delta):
                    if dd < 0:
                        ks.append((c - self.margin * (-dd) - self.margin) // (-dd))
                if ks:
                    k = min(ks)
                    if k > 1:
                        # steps: need second difference; step cost per cycle grows linearly (bounce) -> use d0 steps
                        ds_prev = d0[1]
                        dd_steps = dsteps - ds_prev
                        i = 0
                        for side in (m.L, m.R):
                            for run in side:
                                run[1] += k * delta[i]
                                i += 1
                        # sum_{j=1..k} (dsteps + j*dd_steps)
                        m.steps += k * dsteps + dd_steps * k * (k + 1) // 2
                        self.accel += 1
                        self.hist = {}
                        return
            self.hist[s] = (self.nmacro, v, m.steps, (delta, dsteps))
        else:
            self.hist[s] = (self.nmacro, v, m.steps, None)
        if len(self.hist) > 5000:
            self.hist = {}
        m.step()
        self.nmacro += 1
