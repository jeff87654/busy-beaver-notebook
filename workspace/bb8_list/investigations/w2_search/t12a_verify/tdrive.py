"""tdrive.py MACHINE [maxstages] [pkl]: drive a n1-based machine abstractly from the Coq round-1 end
Bf (FarE k1) [0, 1^w | f] with h14verify's absim (exact tower residues, rank-ordered reps k1 << w << f << later atoms,
Coq CLR / PERIODS macros, affine-uniformity checks on every literal stage).  Only the machine is changed (patched
default of literal_stage).  env as in h14verify: MREP, GROW, REPMODE, MAXS."""
import sys, os, pickle, ctypes
try: ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception: pass
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/t12a_verify/snap')
import absim, drive
from absim import ATOMS, show
M = sys.argv[1]; maxst = int(sys.argv[2]) if len(sys.argv) > 2 else 120
pkl = sys.argv[3] if len(sys.argv) > 3 else 'tdrive.pkl'
d = list(absim.literal_stage.__defaults__); d[0] = M; absim.literal_stage.__defaults__ = tuple(d)
runs, at = drive.round1_end()
if os.environ.get('REAT2'):
    from vals import Val, new_atom, best_res
    _orig = absim.literal_stage
    _fam = {}
    def _conv(v):
        v = Val.of(v)
        if len(v.co) < 2: return v
        key = tuple(sorted(v.co.items()))
        if key not in _fam:
            cint = v.c.numerator // v.c.denominator
            core = v - cint
            r, m = best_res(core)
            dom = max(v.co, key=lambda a: ATOMS[a]['rank'])
            at = new_atom('X', r, m, rank=ATOMS[dom]['rank'] + 0.25, note='reatom %r' % core)
            _fam[key] = (at, core.c)
            print('      reatom %s := %r (res mod %d)' % (ATOMS[list(at.co)[0]]['name'], core, m), flush=True)
        at, c0 = _fam[key]
        return at + (v.c - c0)
    def _lit(runs, *a, **k):
        out = []
        for r in runs:
            if r[0] == 'R': out.append(('R', r[1], _conv(r[2])))
            elif r[0] == 't': out.append(('t', _conv(r[1]), _conv(r[2])))
            else: out.append(('z', _conv(r[1])))
        return _orig(absim.norm(out), *a, **k)
    _lit.__defaults__ = _orig.__defaults__
    drive.literal_stage = _lit
    print('REAT2: multi-atom values replaced by fresh atoms (exact residues, rank just above the dominant atom) before literal stages')
if os.environ.get('PREOK'):
    class _All(set):
        def __contains__(self, x): return True
    absim.PREFIX_OK = _All()   # period macro with any prefix (justified separately: round-2 periods never visit the prefix)
    print('PREOK: PERIOD macro allowed with any left prefix')
print('machine', M); print('MREP', absim.MREP, 'GROW', absim.GROW, 'REPMODE', absim.REPMODE, 'k1 mod 8640', at['k1mod'] % 8640, 'k1 mod 42', at['k1mod'] % 42)
for a, v in ATOMS.items(): print('  atom', v['name'], 'res mod 2520 =', v['res'] % 2520, v['note'])
if os.environ.get('RESUME'):
    import vals
    fn, idx = os.environ['RESUME'].split(':')
    dd = pickle.load(open(fn, 'rb'))
    vals.ATOMS.clear(); vals.ATOMS.update(dd['ATOMS']); vals._next[0] = max(dd['ATOMS']) + 1
    runs = dd['TRAJ'][int(idx) - 1]
    drive.TRAJ.extend(dd['TRAJ'][:int(idx) - 1])
    print('RESUME from', fn, 'stage', idx)
print('start', show(runs), flush=True)
try:
    r = drive.drive(runs, maxst, lambda s: print(s[:900], flush=True))
    print('END', r[0])
    if r[0] == 'HALT': print('final tape', show(r[2], 80))
finally:
    pickle.dump(dict(TRAJ=drive.TRAJ, ATOMS=dict(ATOMS)), open(pkl, 'wb'))
