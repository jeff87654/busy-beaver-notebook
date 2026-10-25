"""Run the planner on every phase of gen_halt.py verbosely (no file output)."""
import planner8 as pl
import gen_halt as g

pl.set_tm(g.TMS)
for name, stmt, start, target in g.PHASES:
    script, cfg = pl.drive(name, start, target, matchers=g.MATCHERS, maxev=400, verbose=True)
    print(script)
print(sorted(pl.LEMMAS))
