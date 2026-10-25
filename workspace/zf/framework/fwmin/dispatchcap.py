"""Dispatch states vs car-run cap, using zf-reduce's ZFP.dechain (imported, not reimplemented) on the
unchanged zf2 program."""
import sys, importlib.util
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\framework\fwmin')
from common import *
spec = importlib.util.spec_from_file_location('zfp', r'C:\Users\jeffr\Downloads\bb8\zf\reduce\zfp.py')
zfp = importlib.util.module_from_spec(spec); spec.loader.exec_module(zfp)

class ZF2D(zf2.ZF2):
    CAP = None; DC_TOP = False
    dechain = zfp.ZFP.dechain
    def build_machine(self):
        self.main(); self.breakout_common_subsequences()
        if self.CAP: self.dechain(self.CAP)
        self.reduce_to_cons(); self.name_sequences(); self.generate(); self.tm.gc(); self.tm.statename = self.tm.start

def build(cap, top=False):
    z = ZF2D(); z.AXIOMORDER = AXIOMORDER; z.CAP = cap; z.DC_TOP = top; z.build_machine(); return z

if __name__ == '__main__':
    for top in (False, True):
        for cap in [None, 9, 8, 7, 6, 5, 4, 3, 2]:
            try:
                z = build(cap, top)
            except (AssertionError, RecursionError) as e:
                print('top' if top else 'deep', cap, 'FAIL', str(e)[:60]); continue
            f, d, t, fw = count(z.tm)
            nd = sum(1 for s in fw if s.startswith('4.dispatch'))
            print('top' if top else 'deep', 'cap', cap, 'framework', f, 'dispatch', nd, 'DAG', d, 'total', t)
