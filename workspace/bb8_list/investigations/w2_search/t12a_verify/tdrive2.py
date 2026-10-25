"""tdrive2.py MACHINE maxst PKL: tdrive (h14verify absim snapshot, exact residues, rank-ordered reps) plus
LOOP ACCELERATION: if three consecutive literal B-form stages have the same run shape and every field changes by the
same integer constant each time, and a huge field decreases, jump N = (that field - margin)/|delta| iterations at once
(this is an induction step; the per-iteration literal stage was uniform in every trial).  env: as tdrive (REAT2, PREOK,
RESUME=pkl:stage, MREP, GROW, MAXS), MARGIN (default 6)."""
import sys, os, pickle, ctypes
try: ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception: pass
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/t12a_verify/snap')
import absim, drive, vals
from absim import ATOMS, show, per_match, is_bform, period_macro, clr, prefix_key, norm
from vals import Val, new_atom, best_res
M = sys.argv[1]; maxst = int(sys.argv[2]); pkl = sys.argv[3]
MARGIN = int(os.environ.get('MARGIN', 6))
d = list(absim.literal_stage.__defaults__); d[0] = M; absim.literal_stage.__defaults__ = tuple(d)
runs, at = drive.round1_end()
class _All(set):
    def __contains__(self, x): return True
if os.environ.get('PREOK'): absim.PREFIX_OK = _All()
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
        a2 = new_atom('X', r, m, rank=ATOMS[dom]['rank'] + 0.25, note='reatom %r' % core)
        _fam[key] = (a2, core.c)
        print('      reatom %s := %r (res mod %d)' % (ATOMS[list(a2.co)[0]]['name'], core, m), flush=True)
    a2, c0 = _fam[key]
    return a2 + (v.c - c0)
def reat(runs):
    if not os.environ.get('REAT2'): return runs
    out = []
    for r in runs:
        if r[0] == 'R': out.append(('R', r[1], _conv(r[2])))
        elif r[0] == 't': out.append(('t', _conv(r[1]), _conv(r[2])))
        else: out.append(('z', _conv(r[1])))
    return norm(out)
TRAJ = []
if os.environ.get('RESUME'):
    fn, idx = os.environ['RESUME'].split(':')
    dd = pickle.load(open(fn, 'rb'))
    vals.ATOMS.clear(); vals.ATOMS.update(dd['ATOMS']); vals._next[0] = max(dd['ATOMS']) + 1
    runs = dd['TRAJ'][int(idx) - 1]; TRAJ.extend(dd['TRAJ'][:int(idx) - 1])
    print('RESUME from', fn, 'stage', idx)
print('machine', M, 'MREP', absim.MREP, 'GROW', absim.GROW, 'REAT2', bool(os.environ.get('REAT2')), 'PREOK', bool(os.environ.get('PREOK')))
print('start', show(runs), flush=True)
def fields(runs):
    f = []
    for r in runs:
        if r[0] == 'R': f.append(Val.of(r[2]))
        elif r[0] == 't': f += [Val.of(r[1]), Val.of(r[2])]
        else: f.append(Val.of(r[1]))
    return f
def shape(runs):
    return tuple((r[0], r[1] if r[0] == 'R' else None) for r in runs)
def setfields(runs, f):
    out = []; i = 0
    for r in runs:
        if r[0] == 'R': out.append(('R', r[1], f[i])); i += 1
        elif r[0] == 't': out.append(('t', f[i], f[i + 1])); i += 2
        else: out.append(('z', f[i])); i += 1
    return norm(out)
def try_loop(hist):
    if len(hist) < 3: return None
    a, b, c = hist[-3:]
    if not (shape(a) == shape(b) == shape(c)): return None
    fa, fb, fc = fields(a), fields(b), fields(c)
    d1 = [y - x for x, y in zip(fa, fb)]; d2 = [y - x for x, y in zip(fb, fc)]
    if any(not x.isconst() for x in d1 + d2) or any(x.c != y.c for x, y in zip(d1, d2)): return None
    if all(x.c == 0 for x in d1): return None
    dec = [(f, -dl.c) for f, dl in zip(fc, d1) if dl.c < 0]
    if not dec or any(not f.huge() for f, _ in dec): return None
    f0, s0 = dec[0]
    for f, s in dec[1:]:
        if dict(f.co) != {k: v * s / s0 for k, v in f0.co.items()} and not (Val.of(f) * s0 - Val.of(f0) * s).isconst(): return None
    # N = (f0 - margin')/s0 with integer constant part
    N = (f0 - MARGIN).div(int(s0)) if s0 != 1 else f0 - MARGIN
    newf = [x + N * dl.c for x, dl in zip(fc, d1)]
    return setfields(c, newf), N
st = len(TRAJ); hist = []
try:
    while st < maxst:
        st += 1; TRAJ.append(runs)
        if is_bform(runs):
            p = period_macro(runs)
            if p and p[0] == 'period':
                runs = p[1]; hist = []
                print('%4d PERIOD J=%r r=%s  -> %s' % (st, p[2]['J'], p[2]['r'], show(runs)), flush=True); continue
            if p and p[0] == 'noinv': print('%4d (Per form, no macro: %s)' % (st, p[1]), flush=True)
            cc = clr(runs)
            if cc and cc[0] == 'clr':
                runs = cc[1]; hist = []
                print('%4d CLR d=%r n=%r A=%r -> new A %r  | %s' % (st, cc[2]['d'], cc[2]['n'], cc[2]['A'], cc[2]['newA'], show(runs)), flush=True); continue
        runs = reat(runs)
        kind, out, info = absim.literal_stage(runs)
        if kind == 'B':
            runs = out
            print('%4d LIT steps=%s t=%.1fs len=%s -> %s' % (st, info['steps'][0], info['time'], info['lens'][0], show(runs)), flush=True)
            hist.append(runs)
            lp = try_loop(hist)
            if lp:
                runs, N = lp; hist = []
                print('%4d LOOP x %r -> %s' % (st, N, show(runs)), flush=True)
        elif kind == 'H':
            print('%4d HALT state %s reads %s, steps=%s; tape %s' % (st, info['q'], info['sym'], info['steps'], show(out, 80)), flush=True)
            print('END HALT'); break
        else:
            print('%4d TIMEOUT steps=%s lens=%s' % (st, info['steps'], info['lens'])); print('END TIMEOUT'); break
    else:
        print('END MAX')
finally:
    pickle.dump(dict(TRAJ=TRAJ, ATOMS=dict(ATOMS)), open(pkl, 'wb'))
