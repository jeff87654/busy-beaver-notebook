import sys, time, random, outl, lowprio, pickle
cls, order = outl.load(sys.argv[1]); secs = float(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
rng = random.Random(seed)
z0 = outl.fresh(cls, order); g0 = outl.G(z0)
best = None; t0 = time.time(); n = 0
while time.time() - t0 < secs:
    g = outl.rgreedy(g0.copy(), rng, topT=rng.choice([20, 40, 80]))
    c = g.cells(); n += 1
    if best is None or c < best[0]:
        z = outl.fresh(cls, order); st = outl.finish(outl.install(z, g))
        best = (c, st); print(n, 'cells', c, 'states', st, f't={time.time()-t0:.0f}', flush=True)
        pickle.dump(g.s, open(sys.argv[1] + '.outl.pkl', 'wb'))
print('runs', n, 'best', best)
