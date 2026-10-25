"""endrun.py: re-run a round-2 end game with explicitly TRUE-ORDER atom ranks on snap3 (current h14verify absim/ures,
RANKMODE=min for new real CLR outputs, plus explicit rank overrides for CLR outputs by note pattern).
Usage: python endrun.py SPEC.py   (SPEC defines M, START (show-string), ATOMS_SPEC {name: (residue, mod, rank)},
OVERRIDE [(regex on CLR note, rank)], MAXST).  env: MREP, GROW, REPMODE, MAXS, MARGIN."""
import sys, os, re, ctypes
try: ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception: pass
os.environ.setdefault('RANKMODE', 'min')
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/t12a_verify/snap3')
import absim, vals, ures
from absim import ATOMS, show, is_bform, clr, norm
from vals import Val, new_atom
spec = {}; exec(open(sys.argv[1]).read(), spec)
M = spec['M']
d = list(absim.literal_stage.__defaults__); d[0] = M; absim.literal_stage.__defaults__ = tuple(d)
AT = {}
for name, (res, mod, rank) in spec['ATOMS_SPEC'].items():
    AT[name] = new_atom(name, res, mod, rank=rank, note='spec')
    ATOMS[list(AT[name].co)[0]]['tier'] = 'real'
def pv(e):
    e = e.strip()
    if e.startswith('(') and e.endswith(')'): e = e[1:-1]
    tot = Val(0)
    for term in re.findall(r'[+-]?[^+-]+', e.replace(' ', '')):
        sg = -1 if term.startswith('-') else 1; t = term.lstrip('+-')
        if '*' in t:
            c, a = t.split('*'); num, _, den = c.partition('/')
            tot = tot + AT[a] * sg * (int(num) if not den else __import__('fractions').Fraction(int(num), int(den)))
        elif t in AT: tot = tot + AT[t] * sg
        else:
            num, _, den = t.partition('/')
            tot = tot + Val(__import__('fractions').Fraction(int(num), int(den) if den else 1) * sg)
    return tot
def parse(s):
    out = []
    for t in re.findall(r'\([^)]*\)\^\(?[^ ]*|\S+\^\([^)]*\)|\([^)]*\)|\S+', s):
        if t.startswith('z'): out.append(('z', Val(int(t[1:])))); continue
        if '^' in t and not t.startswith('('):
            b, c = t.split('^', 1); out.append(('t', pv(b), pv(c))); continue
        out.append(('t', pv(t), Val(1)))
    return norm(out)
runs = parse(spec['START'])
print('machine', M, 'MREP', absim.MREP, 'GROW', absim.GROW, 'REPMODE', absim.REPMODE, 'RANKMODE', os.environ['RANKMODE'])
for k, v in ATOMS.items(): print('  atom', v['name'], 'rank', v['rank'], 'res mod 2520', v['res'] % 2520)
print('start', show(runs, 80), flush=True)
MARGIN = int(os.environ.get('MARGIN', 6))
def fields(r):
    f = []
    for x in r:
        if x[0] == 'R': f.append(Val.of(x[2]))
        elif x[0] == 't': f += [Val.of(x[1]), Val.of(x[2])]
        else: f.append(Val.of(x[1]))
    return f
def shape(r): return tuple((x[0], x[1] if x[0] == 'R' else None) for x in r)
def setf(r, f):
    out = []; i = 0
    for x in r:
        if x[0] == 'R': out.append(('R', x[1], f[i])); i += 1
        elif x[0] == 't': out.append(('t', f[i], f[i + 1])); i += 2
        else: out.append(('z', f[i])); i += 1
    return norm(out)
def try_loop(h):
    if len(h) < 3: return None
    a, b, c = h[-3:]
    if not (shape(a) == shape(b) == shape(c)): return None
    fa, fb, fc = fields(a), fields(b), fields(c)
    d1 = [y - x for x, y in zip(fa, fb)]; d2 = [y - x for x, y in zip(fb, fc)]
    if any(not x.isconst() for x in d1 + d2) or any(x.c != y.c for x, y in zip(d1, d2)) or all(x.c == 0 for x in d1): return None
    dec = [(f, -dl.c) for f, dl in zip(fc, d1) if dl.c < 0]
    if not dec or any(not f.huge() for f, _ in dec): return None
    f0, s0 = dec[0]
    N = (f0 - MARGIN).div(int(s0)) if s0 != 1 else f0 - MARGIN
    return setf(c, [x + N * dl.c for x, dl in zip(fc, d1)]), N
hist = []
for st in range(1, spec.get('MAXST', 120) + 1):
    if is_bform(runs):
        cc = clr(runs)
        if cc and cc[0] == 'clr':
            runs = cc[1]; hist = []
            newA = cc[2]['newA']
            for k in newA.co:
                note = ATOMS[k]['note']
                for pat, rk in spec.get('OVERRIDE', []):
                    if re.search(pat, note): ATOMS[k]['rank'] = rk
            print('%4d CLR d=%r n=%r -> new A %r [tier %s rank %s]  | %s' % (st, cc[2]['d'], cc[2]['n'], newA,
                  ATOMS[list(newA.co)[0]].get('tier') if newA.co else '-', ATOMS[list(newA.co)[0]]['rank'] if newA.co else '-', show(runs, 60)), flush=True)
            continue
    kind, out, info = absim.literal_stage(runs)
    if kind == 'B':
        runs = out; print('%4d LIT steps=%s t=%.1fs len=%s -> %s' % (st, info['steps'][0], info['time'], info['lens'][0], show(runs, 60)), flush=True)
        hist.append(runs); lp = try_loop(hist)
        if lp: runs, N = lp; hist = []; print('%4d LOOP x %r -> %s' % (st, N, show(runs, 60)), flush=True)
    elif kind == 'H':
        print('%4d HALT state %s reads %s, steps=%s' % (st, info['q'], info['sym'], info['steps'])); print('END HALT'); break
    else:
        print('%4d TIMEOUT %s' % (st, info['steps'])); print('END TIMEOUT'); break
else:
    print('END MAX')
