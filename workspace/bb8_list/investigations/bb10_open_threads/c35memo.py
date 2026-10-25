"""Memoised event-level simulation of the c35m14 exception machine (thread 2).
  python c35memo.py "TOKENS" [--r 18] [--maxevents 200000] [--log FILE]
Same event model as c35ev.py (literal event via evt2.exe -j 1, abstract champion clear, accumulator reset to r), but
sub-runs are memoised:  simulate(T, p) runs events while every event changes only indices >= p, and returns the list
at the moment the next event would change an index < p.  The result depends only on T[p-1:] (one token of left
context), which is the memo key.  When an event changes index c >= p, the part right of c is a fresh sub-run:
simulate(T, c+1) is called recursively.  Repeated V-decrement loops then cost one event each after the first.
Events are also cached by their full input list.  Stops at a halt, a timeout, a runaway, or MAXEVENTS literal events.
Prints a trace of the top-level (p = 0) states and summary statistics."""
import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault('EVTEXE', 'evt2.exe')
os.environ.setdefault('JSTOP', '1')
import c35ev  # noqa: E402

sys.setrecursionlimit(100000)


class Stop(Exception):
    pass


class Sim:
    def __init__(self, r, maxevents, log, mv=0):
        self.r, self.maxevents, self.log, self.mv = r, maxevents, log, mv
        self.naccel = 0
        self.ecache, self.memo = {}, {}
        self.nlit = self.nev = self.hits = 0

    def event(self, ts):
        key = tuple(ts)
        if key in self.ecache:
            return self.ecache[key]
        if self.nlit >= self.maxevents:
            raise Stop(f'MAXEVENTS after {self.nlit} literal events')
        self.nlit += 1
        kind, line, _ = c35ev.event(c35ev.M2, list(ts), self.r, 'G', 200_000_000)
        if kind != 'J':
            raise Stop(f'{kind}: {line[:400]}')
        res = c35ev.clear(c35ev.lock_list(line))
        self.ecache[key] = res
        return res

    def accel(self, cur, hist, p, depth):
        """V-loop acceleration: if an earlier loop-top state at this level equals cur except one token (index >= p-1)
        that is now smaller by 3 or 4, shrink that token to (v mod MV) + MV (residue kept mod MV)"""
        for prev in reversed(hist[-60:]):
            if len(prev) != len(cur):
                continue
            diff = [i for i in range(len(cur)) if prev[i] != cur[i]]
            if len(diff) != 1:
                continue
            i = diff[0]
            if i < max(p - 1, 0) or isinstance(cur[i], str) or isinstance(prev[i], str):
                continue
            d = prev[i] - cur[i]
            if d in (3, 4) and cur[i] >= 2 * self.mv:
                new = cur[i] % self.mv + self.mv
                if depth <= 1:
                    self.log(f'    ACCEL depth {depth} index {i}: {cur[i]} -> {new} (drop {d} per loop)')
                self.naccel += 1
                cur = list(cur)
                cur[i] = new
                hist.clear()
                break
        hist.append(tuple(cur))
        return cur

    def simulate(self, ts, p, depth=0):
        """returns the list at the moment the next event would change an index < p"""
        key = (tuple(ts[max(p - 1, 0):]), p > 0)
        start_prefix = ts[:max(p - 1, 0)]
        if key in self.memo:
            self.hits += 1
            return start_prefix + list(self.memo[key])
        cur = list(ts)
        hist = []
        while True:
            if self.mv:
                cur = self.accel(cur, hist, p, depth)
            nxt = self.event(cur)
            self.nev += 1
            c = 0
            while c < len(cur) and c < len(nxt) and cur[c] == nxt[c]:
                c += 1
            if c < p:
                break
            if depth == 0:
                self.log(f'{self.nev:>8} lit={self.nlit:<6} memo={self.hits:<6} c={c:<4} {c35ev.fmt(nxt)}')
            cur = self.simulate(nxt, c + 1, depth + 1)
        self.memo[key] = tuple(cur[max(p - 1, 0):])
        return cur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tokens')
    ap.add_argument('--r', type=int, default=18)
    ap.add_argument('--maxevents', type=int, default=200000)
    ap.add_argument('--log')
    ap.add_argument('--mv', type=int, default=0, help='V-loop acceleration modulus (0 = off)')
    a = ap.parse_args()
    lf = open(a.log, 'w') if a.log else None

    def log(x):
        print(x, flush=True)
        if lf:
            lf.write(x + '\n'); lf.flush()

    sim = Sim(a.r, a.maxevents, log, a.mv)
    ts = c35ev.toks(a.tokens)
    log(f'start {c35ev.fmt(ts)}  r={a.r}')
    try:
        sim.simulate(ts, 0)
        log('returned at top level (an event changed index < 0?)')
    except Stop as ex:
        log(f'STOP {ex}')
    log(f'events={sim.nev} literal={sim.nlit} memo-hits={sim.hits} memo-size={len(sim.memo)} accel={sim.naccel}')


if __name__ == '__main__':
    main()
