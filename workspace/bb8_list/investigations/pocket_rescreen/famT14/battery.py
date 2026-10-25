"""battery.py: canonical macro probes in value form; response signature relative to b."""
from ucode import probe
U = lambda v: (v, 0)
Mk = lambda v: (v, 1)
BAT = [
 ('R2u', [Mk(1), U(2), U(1)]), ('R2m', [Mk(1), U(2), Mk(1)]),
 ('R3k1', [Mk(1), U(2), U(0)]), ('R3k3', [Mk(1), U(2), U(0), U(0), U(0)]), ('R3mx', [Mk(1), Mk(2), U(0), U(0)]),
 ('MZy', [Mk(1), U(1), Mk(0), U(0), U(0)]), ('MZtop', [Mk(0), U(0), U(0)]), ('MZtop1', [Mk(0), U(0)]),
 ('ALL0', [U(0), U(0), U(0)]), ('ALL0m', [Mk(0), U(0), U(0), U(0)]), ('LOWM', [Mk(1), U(1), Mk(0)]),
 ('M0', [Mk(0)]), ('MZMZ', [Mk(1), U(1), Mk(0), Mk(0), U(0), U(0)]), ('MZin', [Mk(1), U(1), U(0), Mk(0), U(0), U(0)]),
 ('Y0', [Mk(1), U(0), Mk(0), U(0), U(0)]),
]
def rel(v, b):
    if isinstance(v, int) and v >= 8: return 'b%+d' % (v - b) if abs(v - b) < 8 else ('2b%+d' % (v - 2 * b) if abs(v - 2 * b) < 12 else 'X%d' % v)
    return str(v)
def resp(C, ds, b):
    o = probe(C, ds, b, N=3 * 10**7, maxev=3000, tmo=15)
    if not o: return 'none'
    o = o[0]
    if o[0] in ('H', 'T'): return o[0]
    out, bb = o
    s = []
    for v, m in out:
        s.append(('M' if m else '') + rel(v, b))
    return ' '.join(s) + ' ;' + rel(bb, b)
def signature(C, bs=(30, 31)):
    sig = {}
    for name, ds in BAT:
        sig[name] = tuple(resp(C, ds, b) for b in bs)
    return sig
