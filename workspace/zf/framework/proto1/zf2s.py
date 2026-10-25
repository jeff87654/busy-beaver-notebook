#!/usr/bin/python3
"""proto1 / F1: Wade's zf2.py with the wff stack held as a STACK OF UNARY REGISTERS instead of a Cantor list.

Registers (index = declaration order, register k = (k+1)-th run from the right):
  0 prooflist 1 nextproof 2 axiomcode 3 param1 4 param2 5 param3 6 scratch1 7 scratch2 8 scratch3
  9 depth (number of real stack entries below top at clause boundaries; only with V['depth'])
  T = 10 top  (always the stack top; = Wade's topwff)      T+1 = 11 second (the entry below top)
  T+2, T+3, ... deeper stack entries, then the zero registers left by boot (and boot's junk run at 68+).

Framework op (TMBuilder.py, gadget 1.q): Q at chain index k
   R_{k+1} == 0 -> MERGE  R_{k+1},R_k into one register R_k + 3 (index k); deeper registers move down
   R_{k+1} != 0 -> INSERT a zero register at index k+1; R_{k+1}.. move up
Program-level stack ops built from it:
   pushwff = top+ ; Q(T-1) [inserts at T since top>=1] ; second-     (new top 0 at T, old top at T+1)
   pop2    = Q(T) [merges since second==0] ; top- top- top-          (drop a ZERO second entry)
Underflow: the original pops 0 from an empty Cantor stack forever; here the region below the real
entries is finite (boot zeros, then boot junk), so cparam pops only if depth>0 (else gives 0).
"""
import TMBuilder
from TMBuilder import subroutine

DEFAULT_VARIANT = dict(
    depth=True,          # exact underflow semantics via a depth register
    select='ifelse',     # 'ifelse' | 'copy' | 'qdrop'
    cons='move_pop',     # 'move_pop' | 'pop_move' | 'pop_clear'
    depth_pos='after',   # depth.inc 'before' | 'after' the default v_0 in main
)


class ZF2S(TMBuilder.TMBuilder):

    def __init__(self, variant=None):
        super().__init__()
        self.V = dict(DEFAULT_VARIANT, **(variant or {}))
        self.prooflist = self.reg("prooflist")
        self.nextproof = self.reg("nextproof")
        self.axiomcode = self.reg("axiomcode")
        self.param1 = self.reg("param1")
        self.param2 = self.reg("param2")
        self.param3 = self.reg("param3")
        self.scratch1 = self.reg("scratch1")
        self.scratch2 = self.reg("scratch2")
        self.scratch3 = self.reg("scratch3")
        if self.V['depth']:
            self.depth = self.reg("depth")
        self.below_top = self.prevreg          # register at index T-1: Q there inserts at T
        self.top = self.reg("top")
        self.second = self.reg("second")
        self.AXIOMORDER = None

    # ---- helpers ----
    def move(self, src, dst):
        return self.while_decnz(src, dst.inc)

    def clear(self, r):
        return self.while_decnz(r, ())

    # ---- stack primitives ----
    @subroutine
    def pushwff(self):
        return [self.top.inc, self.below_top.q, self.second.decnz]

    @subroutine
    def pop2(self):
        # requires second == 0; drops it (Q merges top with the zero below it: top += 3)
        return [self.top.q, self.top.decnz, self.top.decnz, self.top.decnz]

    def v_0(self):
        return self.pushwff()

    @subroutine
    def v_1(self):
        return [*self.v_0(), self.top.inc]

    @subroutine
    def v_2(self):
        return [self.v_0(), [self.top.inc, self.top.inc]]

    @subroutine
    def v_3(self):
        return [self.v_1(), [self.top.inc, self.top.inc]]

    @subroutine
    def v_4(self):
        return [self.v_2(), [self.top.inc, self.top.inc]]

    @subroutine
    def cons(self):
        # top := pair(second, top); drop second
        if self.V['cons'] == 'move_pop':
            return [self.pair(self.scratch2, self.second, self.top),
                    self.move(self.scratch2, self.top),
                    self.pop2()]
        if self.V['cons'] == 'pop_clear':
            # after pair both are 0: Q merges (top := 3), clear it, then move the pair in
            return [self.pair(self.scratch2, self.second, self.top),
                    self.top.q, self.clear(self.top),
                    self.move(self.scratch2, self.top)]
        return [self.pair(self.scratch2, self.second, self.top),
                self.pop2(),
                self.move(self.scratch2, self.top)]

    @subroutine
    def weq(self):
        return [self.cons(), self.v_0(), self.cons()]

    @subroutine
    def wel(self):
        return [self.cons(), self.v_1(), self.cons()]

    @subroutine
    def wim(self):
        return [self.cons(), self.v_2(), self.cons()]

    @subroutine
    def wn(self):
        return [self.v_3(), self.cons()]

    @subroutine
    def wal(self):
        return [self.cons(), self.v_4(), self.cons()]

    @subroutine
    def wex(self):
        return [self.wn(), self.wal(), self.wn()]

    @subroutine
    def wa(self):
        return [self.wn(), self.wim(), self.wn()]

    @subroutine
    def par1(self):
        return [self.pushwff(),
                self.while_decnz(self.param1, [self.top.inc, self.scratch1.inc]),
                self.move(self.scratch1, self.param1)]

    @subroutine
    def par2(self):
        return [self.pushwff(),
                self.while_decnz(self.param2, [self.top.inc, self.scratch1.inc]),
                self.move(self.scratch1, self.param2)]

    @subroutine
    def par3(self):
        return [self.pushwff(),
                self.while_decnz(self.param3, [self.top.inc, self.scratch1.inc]),
                self.move(self.scratch1, self.param3)]

    @subroutine
    def select(self):
        # result := (axiomcode-- > 0) ? top : second ; drop the other
        if self.V['select'] == 'ifelse':
            return [
                self.label("fn", [
                    [self.axiomcode.decnz, [self.clear(self.second), "break_fn"]],
                    [self.clear(self.top), self.move(self.second, self.top)],
                ]),
                self.pop2()]
        if self.V['select'] == 'qdrop':
            # drop second: clear it, Q(T) merges; drop top: clear it, Q(T-1) merges top(0) into R_{T-1}
            bt = self.below_top
            return [
                self.label("fn", [
                    [self.axiomcode.decnz, [[self.clear(self.second), self.pop2()], "break_fn"]],
                    [self.clear(self.top), bt.q, bt.decnz, bt.decnz, bt.decnz],
                ])]
        return [
            self.if_decnz(self.axiomcode, [self.clear(self.second), self.move(self.top, self.second)]),
            self.clear(self.top),
            self.move(self.second, self.top),
            self.pop2()]

    def popparam(self):
        # scratch1 := popped second entry (0 if the theorem stack is empty)
        body = [self.move(self.second, self.scratch1), self.pop2()]
        if self.V['depth']:
            return self.if_decnz(self.depth, body)
        return body

    @subroutine
    def cparam(self, p):
        return [
            self.label("fn", [
                self.label("test", [
                    self.label("innertest", [
                        self.axiomcode.decnz,
                        [
                            [self.axiomcode.decnz,
                             [[self.axiomcode.inc, self.axiomcode.inc], "break_innertest"]],
                            # axiomcode was 1
                            [[self.axiomcode.inc, self.popparam()], "break_test"]
                        ]
                    ]),
                    "break_fn"
                ]),
                [self.clear(p), self.move(self.scratch1, p)]
            ])
        ]

    def axioms(self):
        weq = self.weq(); wel = self.wel(); wim = self.wim(); wn = self.wn(); wal = self.wal()
        wex = self.wex(); wa = self.wa()
        v_0 = self.v_0(); v_1 = self.v_1(); v_2 = self.v_2(); v_3 = self.v_3()
        par1 = self.par1(); par2 = self.par2(); par3 = self.par3()
        select = self.select()
        top = self.top
        return [
            [ # DET
            self.cparam(self.param3), self.cparam(self.param2),
            par3, par1, wim,
            self.while_decnz(top, self.scratch2.inc),
            self.while_decnz(self.param2, [self.scratch1.inc, self.scratch3.inc]),
            self.while_decnz(self.scratch1, self.param2.inc),
            self.if_eq(self.scratch2, self.scratch3, [
                self.while_decnz(self.param1, [self.scratch1.inc, top.inc]),
                self.while_decnz(self.scratch1, self.param1.inc)
                ]),
            select],
            [ # GEN
            self.cparam(self.param3), par1, par3, wal, select],
            [ # B1
            par1, par2, wim, par2, par3, wim, par1, par3, wim, wim, wim, select],
            [ # B2
            par1, wn, par1, wim, par1, wim, select],
            [ # B3
            par1, par1, wn, par2, wim, wim, select],
            [ # B4
            par1, par2, par3, wim, wal, par1, par2, wal, par1, par3, wal, wim, wim, select],
            [ # B6b
            par1, par2, par3, wal, wal, par2, par1, par3, wal, wal, wim, select],
            [ # B8b
            par1, par2, weq, par1, par3, wel, par2, par3, wel, wim, wim, select],
            [ # B6a
            par1, par2, weq, par3, par1, par2, weq, wal, wim,
            par1, par2, wel, par3, par1, par2, wel, wal, wim, wa,
            self.while_decnz(self.param1, [self.scratch1.inc, self.scratch2.inc]),
            self.while_decnz(self.scratch1, self.param1.inc),
            self.while_decnz(self.param3, [self.scratch1.inc, self.scratch3.inc]),
            self.while_decnz(self.scratch1, self.param3.inc),
            self.if_eq(self.scratch2, self.scratch3, [self.while_decnz(top, ())]),
            self.while_decnz(self.param2, [self.scratch1.inc, self.scratch2.inc]),
            self.while_decnz(self.scratch1, self.param2.inc),
            self.while_decnz(self.param3, [self.scratch1.inc, self.scratch3.inc]),
            self.while_decnz(self.scratch1, self.param3.inc),
            self.if_eq(self.scratch2, self.scratch3, [self.while_decnz(top, ())]),
            select],
            [ # B6b
            par1, par2, par3, wal, wal, par2, par1, par3, wal, wal, wim, select],
            [ # B6c
            par1, par1, par2, wal, wex, par2, wim, select],
            [ # B7
            par1, par1, par2, weq, wex, select],
            [ # B8a
            par1, par2, weq, par1, par3, weq, par2, par3, weq, wim, wim, select],
            [ # B8b
            par1, par2, weq, par1, par3, wel, par2, par3, wel, wim, wim, select],
            [ # B8c
            par1, par2, weq, par3, par1, wel, par3, par2, wel, wim, wim, select],
            [ # EXT
            v_2,
            v_2, v_0, wel, v_2, v_1, wel, wim,
            v_2, v_1, wel, v_2, v_0, wel, wim, wa,
            wal, v_0, v_1, weq, wim, select],
            [ # REP
            v_3, v_1, v_2, v_1, par1, wal, v_2, v_1, weq, wim, wal, wex, wal,
            v_1, v_2,
            v_2, v_1, wel, v_3, v_3, v_0, wel, v_1, par1, wal, wa, wex, wim,
            v_3, v_3, v_0, wel, v_1, par1, wal, wa, wex, v_2, v_1, wel, wim, wa,
            wal, wex,
            wim, select],
            [ # POW
            v_1, v_2, v_3, v_3, v_2, wel, v_3, v_0, wel, wim, wal, v_2, v_1, wel, wim, wal, wex, select],
            [ # UNI
            v_1, v_2, v_3, v_2, v_3, wel, v_3, v_0, wel, wa, wex, v_2, v_1, wel, wim, wal, wex, select],
            [# INF
            v_1, v_0, v_1, wel, v_0, v_0, v_1, wel, v_2, v_2, v_1, wel,
            v_1, v_1, v_2, wel, v_1, v_0, weq, wim,
            v_1, v_0, weq, v_1, v_2, wel, wim, wa, wal,
            wa, wex, wim, wal, wa, wex, select],
        ]

    @subroutine
    def main(self):
        AXIOMS = self.axioms()
        if not self.AXIOMORDER:
            self.AXIOMORDER = [x for x in range(len(AXIOMS))]
        dinc = [self.depth.inc] if self.V['depth'] else []
        start = (dinc + [self.v_0()]) if self.V['depth_pos'] == 'before' else ([self.v_0()] + dinc)
        return [
            self.if_not_decnz(self.prooflist, [
                self.while_decnz(self.nextproof, [self.scratch1.inc, self.prooflist.inc]),
                self.while_decnz(self.scratch1, self.nextproof.inc),
                self.nextproof.inc,
                ]),
            self.while_decnz(self.axiomcode, ()),
            self.while_decnz(self.param1, ()),
            self.while_decnz(self.param2, ()),
            self.while_decnz(self.param3, ()),
            self.unpair(self.scratch1, self.scratch2, self.prooflist),
            self.while_decnz(self.scratch2, self.prooflist.inc),
            self.while_decnz(self.scratch1, self.axiomcode.inc),
            self.unpair(self.scratch1, self.scratch2, self.prooflist),
            self.while_decnz(self.scratch2, self.prooflist.inc),
            self.while_decnz(self.scratch1, self.param1.inc),
            self.unpair(self.scratch1, self.scratch2, self.prooflist),
            self.while_decnz(self.scratch2, self.prooflist.inc),
            self.while_decnz(self.scratch1, self.param2.inc),
            self.unpair(self.scratch1, self.scratch2, self.prooflist),
            self.while_decnz(self.scratch2, self.prooflist.inc),
            self.while_decnz(self.scratch1, self.param3.inc),

            *start,   # default theorem if nothing is selected (+ count the pushed theorem)

            *[v for i in self.AXIOMORDER for v in AXIOMS[i]],

            [
                self.top.decnz,
                self.label("if", [
                    [self.top.decnz, [[self.top.inc, self.top.inc], "break_if"]],
                    "halt"
                ])
            ]
        ]


WADE_ORDER = [16, 17, 3, 18, 4, 7, 8, 9, 11, 5, 12, 13, 14, 2, 15, 0, 1, 6, 10, 19]


def count(z):
    st = set(s[0] for s in z.tm.states)
    fw = len([s for s in st if s[0].isdigit()])
    return fw, len(st) - fw, len(st)


def build(order, variant=None):
    z = ZF2S(variant); z.debug = False; z.AXIOMORDER = list(order); z.build_machine()
    return z


if __name__ == "__main__":
    import sys, json
    variant = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    z = build(WADE_ORDER, variant)
    print(count(z))
