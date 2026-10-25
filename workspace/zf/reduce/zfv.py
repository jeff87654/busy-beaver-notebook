"""Variant builder: ZF2 with a configurable clause list (subset of zf2.py's axioms() by index)."""
import zf2

NAMES = ['DET','GEN','B1','B2','B3','B4','B6b','B8b','B6a','B6b','B6c','B7','B8a','B8b','B8c','EXT','REP','POW','UNI','INF']
DEDUP = [i for i in range(20) if i not in (9, 13)]   # drop the second copies of B6b and B8b

class ZFV(zf2.ZF2):
    KEEP = list(range(20))
    def axioms(self):
        a = super().axioms()
        return [a[i] for i in self.KEEP]

def build(order, cls=ZFV, keep=None):
    z = cls()
    if keep is not None: z.KEEP = keep
    z.debug = False; z.AXIOMORDER = list(order); z.build_machine()
    return z

def count(z):
    return len(set(s[0] for s in z.tm.states))

def cost(order, cls=ZFV, keep=None):
    try:
        return count(build(order, cls, keep))
    except (AssertionError, RecursionError):
        return 10**6
