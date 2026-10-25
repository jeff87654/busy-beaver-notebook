"""fwmin variant generator: Wade's zf2 program (imported from ext, unchanged) + a framework variant.

Options (class attributes of FW):
  BOOT  None = Wade's boot (enters 6.continue.4, which is then generated only for the boot).
        (code, exit_state, exit_read, (w, d, target)) = 5-state boot table from boottnf/bootenum, written as
        10 triples 'wdn' for A0 A1 B0 B1 ... E1 (n = 0..4 -> 0.boot.A..E, '---' = exit transition).
  CAP   None or int: zf-reduce's ZFP.dechain car-run cap (changes the DAG, measured only).
Everything else (register chains, 1.*, 2.*, 4.*, 5.*, 6.*) is Wade's framework text verbatim."""
import sys, importlib.util
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\framework\fwmin')
from common import *
import tm as tmmod

BOOTNAMES = ['0.boot.A', '0.boot.B', '0.boot.C', '0.boot.D', '0.boot.E']

def framework_text(boot):
    lines = TMBuilder.framework.splitlines()
    if boot is None:
        return TMBuilder.framework
    code, es, er, (xw, xd, xt) = boot
    out = []
    for l in lines:
        if l.startswith('0.boot.'): continue
        out.append(l)
        if l.startswith('# 0. boot'):
            out.append('#')
            out.append('# fwmin boot (5 states, found by fwmin/boottnf.c); exit enters %s' % xt)
            for i, nm in enumerate(BOOTNAMES):
                for r in '01':
                    tr = code[3 * (2 * i + int(r)): 3 * (2 * i + int(r)) + 3]
                    if tr == '---' or (i == es and int(r) == er):
                        out.append(f'{nm} {r} {xw} {xd} {xt}')
                    else:
                        out.append(f'{nm} {r} {tr[0]} {tr[1]} {BOOTNAMES[int(tr[2])]}')
    return '\n'.join(out)

_zfp = None
def zfp():
    global _zfp
    if _zfp is None:
        spec = importlib.util.spec_from_file_location('zfp', r'C:\Users\jeffr\Downloads\bb8\zf\reduce\zfp.py')
        _zfp = importlib.util.module_from_spec(spec); spec.loader.exec_module(_zfp)
    return _zfp

class FW(zf2.ZF2):
    BOOT = None
    CAP = None
    DC_TOP = False

    def build_machine(self):
        self.main()
        self.breakout_common_subsequences()
        if self.CAP:
            zfp().ZFP.dechain(self, self.CAP)
        self.reduce_to_cons()
        self.name_sequences()
        self.generate()
        self.tm.gc()
        self.tm.statename = self.tm.start

    def generate(self):
        T = tmmod.Transition
        def consecutive_zeros(v):
            return 1 + consecutive_zeros(self.sequences[v].seq[0]) if isinstance(v, int) else 0
        def generate_break(level):
            while level > 0:
                self.tm.states[(f"6.break.{level}", "0")] = T("0", "L", f"6.break.{level - 1}")
                self.tm.states[(f"6.break.{level}", "1")] = T("0", "L", f"6.break.{level}")
                level -= 1
        def generate_continue(level):
            while level > 0:
                self.tm.states[(f"6.continue.{level}", "0")] = T("0", "L", f"6.continue.{level}")
                self.tm.states[(f"6.continue.{level}", "1")] = T("0", "L", f"6.continue.{level - 1}")
                level -= 1
        max_zeros = max(2, max(consecutive_zeros(i) for i in self.reachable()))
        for lineno, l in enumerate(framework_text(self.BOOT).splitlines()):
            self.tm.loadline(l, "<framework>", lineno)
        for i in range(2, max_zeros):
            self.tm.states[(f"4.dispatch.{i}", "0")] = T("0", "L", f"4.dispatch.{i+1}")
            self.tm.states[(f"4.dispatch.{i}", "1")] = T("1", "L", "6.continue.0")
        self.tm.states[(f"4.dispatch.{max_zeros}", "0")] = T("0", "R", "5.root")
        self.tm.states[(f"4.dispatch.{max_zeros}", "1")] = T("1", "L", "6.continue.0")
        if self.BOOT is None:
            generate_continue(4)          # Wade's boot enters 6.continue.4
        else:                             # the boot may enter a break/continue state: make sure it exists
            xt = self.BOOT[3][2]
            if xt.startswith('6.break.'): generate_break(int(xt.split('.')[2]))
            if xt.startswith('6.continue.'): generate_continue(int(xt.split('.')[2]))
        for seq_i in self.reachable():
            seq = self.sequences[seq_i]
            a, b = seq.seq
            if isinstance(a, int):
                self.tm.states[(seq.name, "0")] = T("0", "R", self.sequences[a].name)
            elif a.startswith("_break."):
                if a == "_break.0":
                    self.tm.states[(seq.name, "0")] = T("1", "L", "6.continue.0")
                else:
                    k = int(a.split(".")[1]) - 1
                    self.tm.states[(seq.name, "0")] = T("0", "L", f"6.break.{k}"); generate_break(k)
            elif a.startswith("_continue."):
                k = int(a.split(".")[1])
                self.tm.states[(seq.name, "0")] = T("0", "L", f"6.continue.{k}"); generate_continue(k)
            else:
                self.tm.states[(seq.name, "0")] = T("0", "R", a)
            if isinstance(b, int):
                self.tm.states[(seq.name, "1")] = T("1", "R", self.sequences[b].name)
            elif b.startswith("_break."):
                k = int(b.split(".")[1])
                self.tm.states[(seq.name, "1")] = T("0", "L", f"6.break.{k}"); generate_break(k)
            elif b.startswith("_continue."):
                k = int(b.split(".")[1]) - 1
                assert k >= 0
                self.tm.states[(seq.name, "1")] = T("0", "L", f"6.continue.{k}"); generate_continue(k)
            else:
                self.tm.states[(seq.name, "1")] = T("1", "R", b)

def build(boot=None, cap=None):
    class V(FW): pass
    V.BOOT = boot; V.CAP = cap
    z = V(); z.AXIOMORDER = AXIOMORDER; z.build_machine(); return z

def emit(z, path):
    z.tm.save(path)
    return count(z.tm)

if __name__ == '__main__':
    z = build()
    f, d, t, fw = emit(z, HERE + r'\v0_wade.tm')
    print('wade-equivalent', f, d, t)
