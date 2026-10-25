import sys, outl, lowprio
cls, order = outl.load(sys.argv[1])
z = outl.fresh(cls, order)
g = outl.G(z); print('raw cells', g.cells(), flush=True)
topT = int(sys.argv[2]) if len(sys.argv) > 2 else 60
g = outl.greedy(g, topT=topT, verbose=False)
print('greedy cells', g.cells(), flush=True)
print('states', outl.finish(outl.install(z, g)))
