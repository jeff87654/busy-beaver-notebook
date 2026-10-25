"""Finite-frame test for the X6 question (modal abstraction with two variables y, z).
Frame: worlds 0..n-1, relations Ry, Rz (sets of pairs).  Conditions modelling the rest of the system:
  X6(u,v) for u,v in {y,z}:  (Ru;Rv)^-1 included in Ru;Rv        [E.u E.v A.u A.v a -> a]
  seriality of Ry, Rz                                              [B7 gives E.u T]
Valuation of a letter p that is y-vacuous: p true at w and w Ry w' => p at w' (B6a-like; with X6 this
makes -.p persistent too).  Goal instance of lvac's Wal case: A.z p -> A.y A.z p.  Also tests B6c for
z on arbitrary valuations (frame symmetry of Rz is what B6c needs).  usage: python frames.py N"""
import sys, itertools
sys.path.insert(0, '..'); import lowprio  # noqa
n = int(sys.argv[1]); W = range(n)
pairs = [(a, b) for a in W for b in W]
def comp(R, S): return {(a, c) for (a, b) in R for (b2, c) in S if b == b2}
def inv(R): return {(b, a) for (a, b) in R}
def serial(R): return all(any((a, b) in R for b in W) for a in W)
rels = []
for bits in itertools.product((0, 1), repeat=n * n):
    R = {p for p, bt in zip(pairs, bits) if bt}
    if serial(R) and inv(comp(R, R)) <= comp(R, R): rels.append(frozenset(R))
print('candidate single relations', len(rels), flush=True)
found = 0
for Ry in rels:
    for Rz in rels:
        if not inv(comp(Ry, Rz)) <= comp(Ry, Rz): continue
        if not inv(comp(Rz, Ry)) <= comp(Rz, Ry): continue
        sym_z = Rz == inv(Rz); sym_y = Ry == inv(Ry); comm = comp(Ry, Rz) == comp(Rz, Ry)
        # valuations p persistent along Ry
        for pv in itertools.product((0, 1), repeat=n):
            if any(pv[a] and not pv[b] for (a, b) in Ry): continue
            boxz = [all(pv[b] for (a, b) in Rz if a == w) for w in W]
            boxyboxz = [all(boxz[b] for (a, b) in Ry if a == w) for w in W]
            bad = [w for w in W if boxz[w] and not boxyboxz[w]]
            if bad:
                print('WAL-CASE FAILS: Ry', sorted(Ry), 'Rz', sorted(Rz), 'p', pv, 'at', bad, flush=True)
                found += 1
                if found > 3: sys.exit()
        if not sym_z or not sym_y or not comm:
            if found < 6:
                print('asym/noncomm frame: Ry', sorted(Ry), 'Rz', sorted(Rz), 'symy', sym_y, 'symz', sym_z, 'comm', comm, flush=True)
                found += 1
print('done', found)
