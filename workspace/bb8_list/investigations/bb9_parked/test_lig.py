"""test_lig.py MACHINE WORDFILE STEPS [BS]: Ligocki block sim (as installed by lkf) vs literal, from word+head-at-end state B"""
import sys, importlib.util
spec = importlib.util.spec_from_file_location('lkf', 'lkf.py'); L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
m, wf, N = sys.argv[1], sys.argv[2], int(sys.argv[3]); bs = int(sys.argv[4]) if len(sys.argv) > 4 else 6
w = open(wf).read().strip()
class A: pass
a = A(); a.machine = m; a.bs = bs; a.noprover = True; a.recursive = False; a.Rs = ''; a.u = '10'; a.S1 = '11'; a.tunit = '11111100'; a.S2 = '1001'; a.beta = 2; a.rc = 4
F = L.Follower(a); F.install(L.norm([(ch, 1) for ch in w]), 1)
sim = F.sim
while sim.step_num < N:
    sim.step()
print('lig step', sim.step_num, 'dir', sim.tape.dir, 'state', int(sim.state))
at = L.norm(F.left_atoms() + F.right_atoms()); s = ''.join(p * c for p, c in at).strip('0')
# literal
ns, T = L.parse_tm(m); tape = {i: int(ch) for i, ch in enumerate(w)}; h = len(w); q = 1
for st in range(int(sim.step_num)):
    c = tape.get(h, 0); tr = T[(q, c)]; tape[h] = tr[0]; h += tr[1]; q = tr[2]
lo = min(k for k in tape if tape[k]); hi = max(k for k in tape if tape[k])
s2 = ''.join(str(tape.get(i, 0)) for i in range(lo, hi + 1))
print('equal', s == s2, len(s), len(s2)); print(s[-100:]); print(s2[-100:])
