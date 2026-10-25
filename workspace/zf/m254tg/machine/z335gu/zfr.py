"""Reduced ZF machine program: zf2.py's subroutines, clause table by name, optional program changes (OPT)."""
import zf2
from TMBuilder import subroutine

BASE = ['DET','GEN','B1','B2','B3','B4','B6b','B8b','B6a','B6c','B7','B8a','B8c','EXT','REP','POW','UNI','INF']
PREMISE = {'DET', 'GEN'}   # premise-consuming clauses: must not be last in the order

class ZFR(zf2.ZF2):
    CLAUSES = BASE
    OPT = frozenset()

    def clause(self, name):
        weq = self.weq(); wel = self.wel(); wim = self.wim(); wn = self.wn(); wal = self.wal()
        wex = self.wex(); wa = self.wa()
        v_0 = self.v_0(); v_1 = self.v_1(); v_2 = self.v_2(); v_3 = self.v_3()
        par1 = self.par1(); par2 = self.par2(); par3 = self.par3()
        select = self.select()
        s1, s2, s3 = self.scratch1, self.scratch2, self.scratch3
        p1, p2, p3, tw = self.param1, self.param2, self.param3, self.topwff
        W = self.while_decnz
        if name == 'DET':
            return [self.cparam(p3), self.cparam(p2), par3, par1, wim,
                    W(tw, s2.inc), W(p2, [s1.inc, s3.inc]), W(s1, p2.inc),
                    self.if_eq(s2, s3, [W(p1, [s1.inc, tw.inc]), W(s1, p1.inc)]),
                    select]
        if name == 'GEN': return [self.cparam(p3), par1, par3, wal, select]
        if name == 'B1': return [par1, par2, wim, par2, par3, wim, par1, par3, wim, wim, wim, select]
        if name == 'B2': return [par1, wn, par1, wim, par1, wim, select]
        if name == 'B3': return [par1, par1, wn, par2, wim, wim, select]
        if name == 'B4': return [par1, par2, par3, wim, wal, par1, par2, wal, par1, par3, wal, wim, wim, select]
        if name == 'B6b': return [par1, par2, par3, wal, wal, par2, par1, par3, wal, wal, wim, select]
        if name == 'B8b': return [par1, par2, weq, par1, par3, wel, par2, par3, wel, wim, wim, select]
        if name == 'B6a':
            body = [par1, par2, weq, par3, par1, par2, weq, wal, wim,
                    par1, par2, wel, par3, par1, par2, wel, wal, wim, wa]
            if 'nocheck' in self.OPT:      # MEASUREMENT ONLY (unsound)
                return body + [select]
            return body + [
                W(p1, [s1.inc, s2.inc]), W(s1, p1.inc), W(p3, [s1.inc, s3.inc]), W(s1, p3.inc),
                self.if_eq(s2, s3, [W(tw, ())]),
                W(p2, [s1.inc, s2.inc]), W(s1, p2.inc), W(p3, [s1.inc, s3.inc]), W(s1, p3.inc),
                self.if_eq(s2, s3, [W(tw, ())]),
                select]
        if name == 'B6c': return [par1, par1, par2, wal, wex, par2, wim, select]
        if name == 'B7': return [par1, par1, par2, weq, wex, select]
        if name == 'B8a': return [par1, par2, weq, par1, par3, weq, par2, par3, weq, wim, wim, select]
        if name == 'B8c': return [par1, par2, weq, par3, par1, wel, par3, par2, wel, wim, wim, select]
        if name == 'EXT':
            return [v_2, v_2, v_0, wel, v_2, v_1, wel, wim, v_2, v_1, wel, v_2, v_0, wel, wim, wa,
                    wal, v_0, v_1, weq, wim, select]
        if name == 'REP':
            return [v_3, v_1, v_2, v_1, par1, wal, v_2, v_1, weq, wim, wal, wex, wal,
                    v_1, v_2,
                    v_2, v_1, wel, v_3, v_3, v_0, wel, v_1, par1, wal, wa, wex, wim,
                    v_3, v_3, v_0, wel, v_1, par1, wal, wa, wex, v_2, v_1, wel, wim, wa,
                    wal, wex, wim, select]
        if name == 'POW':
            return [v_1, v_2, v_3, v_3, v_2, wel, v_3, v_0, wel, wim, wal, v_2, v_1, wel, wim, wal, wex, select]
        if name == 'UNI':
            return [v_1, v_2, v_3, v_2, v_3, wel, v_3, v_0, wel, wa, wex, v_2, v_1, wel, wim, wal, wex, select]
        if name == 'INF':
            return [v_1, v_0, v_1, wel, v_0, v_0, v_1, wel, v_2, v_2, v_1, wel,
                    v_1, v_1, v_2, wel, v_1, v_0, weq, wim,
                    v_1, v_0, weq, v_1, v_2, wel, wim, wa, wal,
                    wa, wex, wim, wal, wa, wex, select]
        raise KeyError(name)

    def axioms(self):
        return [self.clause(n) for n in self.CLAUSES]

def make(clauses=BASE, opt=()):
    class V(ZFR):
        pass
    V.CLAUSES = list(clauses); V.OPT = frozenset(opt)
    return V
