# kgval.py FITTED_TSV N SEED [LITBUDGET] : validate the template engine (R1ITER / CDP jumps) against lit.
# For N machines with supported templates (plus the BB(7) champion), runs small K(ds; a; b) start configurations
# with symsim --tmpl (grid-checked) and with lit; every lit halter must be a symsim HALT with equal sigma and tape,
# no symsim CYCLE may halt literally.
import sys, random, subprocess, os, collections
D = os.path.dirname(os.path.abspath(__file__))
SYM, LIT = os.path.join(D, os.environ.get('SYMEXE', 'symsim_v9.exe')), os.path.join(D, 'lit.exe')
fn, N, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); litb = sys.argv[4] if len(sys.argv) > 4 else '3000000000'
random.seed(seed)
CH = ('1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF', 'R,B,P=11,u=10,s=1,d=3d+1,b=3b+2,S=111001')
rows = [l.rstrip('\n').split('\t') for l in open(fn)]
ok = [r for r in rows if r[4].startswith('R1 2b+2 | R2 a=2b+2 b=0 | R3 2b+2+0k tail=0 a=0 b=0') and ',d=3d+1,' in r[3] and ',b=3b+' in r[3] and not r[3].endswith('S=-')]
pick = [CH] + [(r[0], r[3]) for r in random.sample(ok, min(N, len(ok)))]
confs = [([1], 0, 0), ([1], 1, 0), ([1], 0, 1), ([1], 0, 2), ([1, 1], 0, 0), ([2], 0, 0), ([0, 1], 0, 0), ([1], 2, 1), ([1, 0, 1], 0, 0)]
C = collections.Counter(); bad = []
for m, t in pick:
    f = dict(x.split('=', 1) for x in t.split(',')[2:] if '=' in x); Q = t.split(',')[1]
    P, u, S, beta = f['P'], f['u'], f['S'], int(f['b'][3:])
    specs = []
    for ds, a, b in confs:
        w = [P] + [f'{u}^{3*d+1} 1' for d in reversed(ds)] + [f'{u}^{3*a+1} 1', f'{u}^{3*b+beta}' if 3*b+beta > 0 else '', S, f'{Q}>']
        specs.append(' '.join(x for x in w if x))
    inp = ''.join(f'{m} {Q} {sp}\n' for sp in specs)
    so = subprocess.run([SYM, 'run', '--tmpl', t, '--tape', '--budget', '300000', '--tlimit', '20', '--sigwin', '0'] + os.environ.get('SYMOPTS', '').split(), input=inp, capture_output=True, text=True)
    lo = subprocess.run([LIT, litb], input=inp, capture_output=True, text=True).stdout.split('\n')
    sl = so.stdout.split('\n'); S2 = []; i = 0
    while i < len(sl):
        if sl[i].startswith('R '): S2.append((sl[i].split(), sl[i + 1])); i += 2
        else: i += 1
    L2 = []; i = 0
    while i < len(lo):
        if lo[i].startswith('L '): L2.append((lo[i].split(), lo[i + 1])); i += 2
        else: i += 1
    ruled = 'RULED' in so.stderr and 'UNRULED' not in so.stderr
    C['machines ' + ('RULED' if ruled else 'UNRULED')] += 1; print('#', m, 'RULED' if ruled else 'UNRULED', flush=True)
    for sp, (s, st), (l, lt) in zip(specs, S2, L2):
        sig = [x for x in s if x.startswith('sigma=')][0][6:]; kj = int([x for x in s if x.startswith('kj=')][0][3:])
        C[f'lit={l[3]} sym={s[3]}' + (' (jumped)' if kj else '')] += 1
        if l[3] == 'HALT':
            if s[3] == 'CYCLE': bad.append(('UNSOUND', m, sp))
            elif s[3] == 'HALT' and (sig != l[5] or st != lt): bad.append(('mismatch', m, sp, sig, l[5]))
            elif s[3] == 'HALT' and kj: C['halt match after jumps'] += 1
for k, v in sorted(C.items()): print(f'{v:7d} {k}')
print('BAD', len(bad)); [print(' ', b) for b in bad[:20]]
