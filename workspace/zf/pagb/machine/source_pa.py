"""ZFC-targeted consistency search with 11 axiom families.
Four-constructor base-four formula coding; 0 is truth and 1 is closed falsity.
Negation is implication to 1. Data use dual Cantor pairing.
Finite theorem-stack command programs, binary blank tape. Not kernel-certified."""
import TMBuilder
from TMBuilder import subroutine

class ZF2(TMBuilder.TMBuilder):

    def __init__(self):
        super().__init__()
        for name in ['nextproof', 'topwff', 'wffstack', 'axiomcode', 'param1', 'param2', 'scratch1', 'scratch2', 'prooflist']:
            setattr(self, name, self.reg(name))
        self.param3 = self.axiomcode

    @subroutine
    def pushwff(self):
        return [self.while_decnz(self.topwff, self.scratch1.inc), self.while_decnz(self.wffstack, self.topwff.inc), self.pair(self.scratch2, self.scratch1, self.topwff), self.while_decnz(self.scratch2, self.wffstack.inc)]

    def v_0(self):
        return self.pushwff()

    @subroutine
    def v_1(self):
        return [*self.v_0(), self.topwff.inc]

    @subroutine
    def v_2(self):
        return [*self.v_1(), self.topwff.inc]

    @subroutine
    def v_3(self):
        return [*self.v_2(), self.topwff.inc]

    @subroutine
    def v_4(self):
        return [*self.v_3(), self.topwff.inc]

    @subroutine
    def cons(self):
        return [self.unpair(self.scratch1, self.scratch2, self.wffstack), self.while_decnz(self.scratch2, self.wffstack.inc), self.pair(self.scratch2, self.scratch1, self.topwff), self.times_from_scratch()]

    @subroutine
    def weq(self):
        return [self.cons(), self.topwff.inc, self.topwff.inc, self.topwff.inc]

    @subroutine
    def wel(self):
        return [self.cons(), self.topwff.inc]

    @subroutine
    def wim(self):
        return [self.cons()]

    @subroutine
    def wn(self):
        return [self.v_1(), self.wim()]

    @subroutine
    def wal(self):
        return [self.cons(), self.topwff.inc, self.topwff.inc]

    @subroutine
    def wex(self):
        return [self.wn(), *self.wal(), self.wn()]

    @subroutine
    def wa(self):
        return [self.wn(), *self.wim(), self.wn()]

    @subroutine
    def occ_init(self):
        return [self.param1.inc, self.pair(self.scratch1, self.param1, self.scratch2),
                self.param2.inc, self.pair(self.param1, self.param2, self.scratch1)]

    @subroutine
    def occ_pop(self):
        return [self.unpair(self.param2, self.scratch1, self.param1), self.while_decnz(self.scratch1, self.param1.inc)]

    @subroutine
    def occ_push_j(self):
        return [self.param2.inc, self.pair(self.scratch1, self.param2, self.param1), self.while_decnz(self.scratch1, self.param1.inc)]


    @subroutine
    def occ_jk(self):
        return [self.unpair(self.param2, self.scratch2, self.scratch1)]

    @subroutine
    def occ_h_sigma(self):
        return [self.occ_jk(), self.while_decnz(self.scratch2, ()), self.occ_push_j()]

    @subroutine
    def occ_h_bin(self):
        return [self.occ_jk(), self.occ_push_j(), self.while_decnz(self.scratch2, self.param2.inc), self.occ_push_j1()]

    @subroutine
    def occ_push_j1(self):
        return [self.occ_push_j()]

    @subroutine
    def occ_h_var(self):
        return [self.occ_jk(), self.while_decnz(self.scratch2, ()),
                self.while_decnz(self.param3, [self.scratch1.inc, self.scratch2.inc]),
                self.while_decnz(self.scratch2, self.param3.inc),
                self.if_eq(self.param2, self.scratch1, [self.while_decnz(self.topwff, ())])]

    def occ_dm(self):
        x, q = self.param2, self.scratch1
        s3 = [[x.decnz, [q.inc, 'continue_dm']], [self.occ_h_var(), 'break_dm']]
        s2 = [[x.decnz, s3], [self.occ_h_bin(), 'break_dm']]
        s1 = [[x.decnz, s2], [self.occ_h_bin(), 'break_dm']]
        s0 = [[x.decnz, s1], self.occ_h_sigma()]
        return self.label('dm', s0)

    @subroutine
    def occgate(self):
        x = self.param2
        item = [x.decnz, [x.inc, self.occ_dm()]]          # x = 0 (zero term): skip
        walk = self.label('walk', [self.occ_pop(), [x.decnz, [[item], 'continue_walk']]])
        return [self.occ_init(), walk, self.while_decnz(self.param3, ())]

    @subroutine
    def par1(self):
        return [self.pushwff(), self.while_decnz(self.param1, [self.scratch1.inc, self.topwff.inc]), self.while_decnz(self.scratch1, self.param1.inc)]

    @subroutine
    def par2(self):
        return [self.pushwff(), self.while_decnz(self.param2, [self.scratch1.inc, self.topwff.inc]), self.while_decnz(self.scratch1, self.param2.inc)]

    @subroutine
    def par3(self):
        return [self.pushwff(), self.while_decnz(self.param3, [self.scratch1.inc, self.topwff.inc]), self.while_decnz(self.scratch1, self.param3.inc)]

    @subroutine
    def select(self):
        return [self.unpair(self.scratch1, self.scratch2, self.wffstack), self.while_decnz(self.scratch2, self.wffstack.inc), self.if_not_decnz(self.axiomcode, [self.while_decnz(self.topwff, ()), self.while_decnz(self.scratch1, self.topwff.inc)]), self.while_decnz(self.scratch1, ())]

    @subroutine
    def unpair(self, out1, out2, in1):
        return [self.while_decnz(in1, [out2.inc, self.if_not_decnz(out1, self.while_decnz(out2, out1.inc))])]

    @subroutine
    def read(self, out):
        return [self.unpair(self.scratch1, self.scratch2, self.prooflist), self.while_decnz(self.scratch2, self.prooflist.inc), self.while_decnz(self.scratch1, out.inc)]

    @subroutine
    def pop(self, out):
        return [self.unpair(self.scratch1, self.scratch2, self.wffstack), self.while_decnz(self.scratch2, self.wffstack.inc), self.while_decnz(self.scratch1, out.inc)]

    @subroutine
    def gen(self):
        return [self.unpair(self.scratch1, self.scratch2, self.prooflist), self.while_decnz(self.scratch2, self.prooflist.inc), self.pair(self.scratch2, self.scratch1, self.topwff), self.times_from_scratch(), self.topwff.inc, self.topwff.inc]

    @subroutine
    def mp(self):
        return [self.par1(), self.wim(), self.while_decnz(self.topwff, self.scratch1.inc), self.if_eq(self.scratch1, self.param2, [self.par1()])]

    @subroutine
    def drop(self):
        return [self.par2()]

    @subroutine
    def nip(self):
        return [self.scratch1.inc, self.if_eq(self.scratch1, self.param2, ['halt']), self.pop(self.param2)]

    @subroutine
    def axioms(self):
        weq = self.weq()
        wel = self.wel()
        wim = self.wim()
        wn = self.wn()
        wal = self.wal()
        wex = self.wex()
        wa = self.wa()
        v_0 = self.v_0()
        v_1 = self.v_1()
        v_2 = self.v_2()
        v_3 = self.v_3()
        v_4 = self.v_4()
        par1 = self.par1()
        par2 = self.par2()
        par3 = self.par3()
        return [par1, par2, wal, self.read(self.param2), par1, v_0, weq, v_1, wim, par2, v_0, weq, wel, par1, v_0, weq, par2, v_0, weq, wel, v_1, wim, weq, par1, v_0, weq, v_1, wim, par2, v_0, weq, v_1, wim, weq, par1, v_0, weq, par2, v_0, weq, weq, wim, par1, par1, par2, wal, wex, par2, wim, par1, par2, weq, par1, par3, wal, par2, par3, wal, weq, wim, v_4, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, v_2, v_4, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, v_0, weq, v_2, v_0, weq, v_2, v_0, weq, wel, weq, wn, wal, wn, v_2, v_4, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, v_0, weq, v_0, v_1, wim, v_1, wim, v_1, wim, v_1, wim, v_2, v_0, weq, wel, weq, wn, wal, wn, wn, wim, wn, v_4, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, v_4, self.topwff.inc, self.topwff.inc, v_2, v_4, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, v_0, weq, v_0, v_1, wim, v_1, wim, v_2, v_0, weq, wel, weq, wn, wal, wn, v_4, v_2, v_4, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, v_0, weq, v_4, v_0, weq, v_2, v_0, weq, wal, weq, v_4, v_0, weq, v_0, v_1, wim, weq, wn, v_2, v_0, weq, v_0, v_1, wim, weq, wim, wim, wal, wal, wn, wim, wn, v_2, v_4, self.topwff.inc, self.topwff.inc, v_0, weq, v_0, v_1, wim, v_1, wim, v_2, v_0, weq, wel, weq, wn, wal, wn, v_4, v_2, v_4, self.topwff.inc, self.topwff.inc, v_0, weq, v_4, v_0, weq, v_2, v_0, weq, wal, weq, v_4, v_0, weq, v_0, v_1, wim, weq, wn, v_2, v_0, weq, v_0, v_1, wim, weq, wim, wim, wal, wal, wn, wim, wn, wn, wim, wn, v_4, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, v_0, weq, v_4, self.topwff.inc, self.topwff.inc, v_0, weq, wel, v_4, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, v_0, weq, weq, wn, wim, wn, wn, wal, wn, wn, wal, wn, wim, wal, wn, par1, v_0, weq, v_1, wim, par2, v_0, weq, wal, par2, v_0, weq, par1, v_0, weq, par2, v_0, weq, wal, wel, weq, par3, self.topwff.inc, par3, self.topwff.inc, v_0, weq, par3, weq, wex, par1, par2, weq, par1, v_1, wim, par2, v_1, wim, weq, wim, par1, par2, weq, par1, par3, wel, par2, par3, wel, weq, wim, par1, par2, par3, wal, wal, par2, par1, par3, wal, wal, wim, v_0, par3, v_0, weq, wel, par3, v_0, weq, weq, par3, self.pushwff(), self.unpair(self.scratch1, self.scratch2, self.prooflist), self.while_decnz(self.scratch2, self.prooflist.inc), self.while_decnz(self.scratch1, self.topwff.inc), wim, par1, wim, par1, par3, wim, par2, par3, wim, wim, wim, par1, par2, weq, par3, par1, wal, par3, par2, wal, weq, wim, par3, par1, weq, par3, par2, weq, par1, par2, weq, wim, wim, par1, par2, weq, par3, par1, wel, par3, par2, wel, weq, wim, par1, par2, par3, wim, wal, par1, par2, wal, par1, par3, wal, wim, wim, par1, par1, v_0, weq, par2, v_0, weq, weq, wex, v_0, par1, v_0, weq, wal, v_0, weq, v_0, par1, v_0, weq, v_1, wim, weq, wn, par1, par1, v_0, weq, v_0, weq, par3, wim, wal, par1, par3, par3, par3, v_0, weq, par1, v_0, weq, v_1, wim, weq, par1, par1, v_0, weq, par3, v_0, weq, weq, par3, wim, wal, wim, wal, wim, wal, par1, par3, wal, wim, wim, par1, par2, weq, par3, par1, par2, weq, wal, wim, wa, self.occgate()]

    @subroutine
    def if_eq(self, in1, in2, body):
        return [self.label('fn', [[self.label('loop', [in1.decnz, [[in2.decnz, 'continue_loop'], [self.while_decnz(in1, in2.inc), in2.inc]]]), [in2.decnz, [self.while_decnz(in2, ()), 'break_fn']]], body])]

    def dispatch(self, actions):
        if len(actions) == 1:
            return actions[0]
        return self.label('switch', [[self.axiomcode.decnz, [self.dispatch(actions[1:]), 'break_switch']], actions[0]])

    @subroutine
    def main(self):
        return [self.if_not_decnz(self.prooflist, [self.while_decnz(self.nextproof, [self.prooflist.inc, self.scratch1.inc]), self.while_decnz(self.scratch1, self.nextproof.inc), self.nextproof.inc]), self.read(self.axiomcode), self.read(self.param1), self.dispatch([self.mp(), self.drop(), self.nip(), self.axioms()])]

    @subroutine
    def times(self):
        return [self.while_decnz(self.topwff, self.scratch2.inc), self.times_from_scratch()]

    @subroutine
    def times_from_scratch(self):
        return [self.while_decnz(self.scratch2, [self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc])]

    @subroutine
    def pair(self, out, in1, in2):
        return [self.label('loop', [self.while_decnz(in2, [in1.inc, out.inc]), [in1.decnz, [[out.inc, self.while_decnz(in1, in2.inc)], 'continue_loop']]])]

    @subroutine
    def load_5(self):
        return [self.pushwff(), self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc, self.topwff.inc]
