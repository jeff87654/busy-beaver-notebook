# affcheck.py N SEED : random 2..6-state machines; those whose symsim run applies affine rules are re-run literally.
# Every literal halter must be a symsim HALT with the same sigma and final tape; no symsim CYCLE may halt literally.
import sys, random, subprocess, os, collections
D = os.path.dirname(os.path.abspath(__file__))
SYM, LIT = os.path.join(D, os.environ.get('SYMEXE', 'symsim_v8b.exe')), os.path.join(D, 'lit.exe')
N, seed = int(sys.argv[1]), int(sys.argv[2]); random.seed(seed)
def rslot(ns): return random.choice('01') + random.choice('LR') + chr(65 + random.randrange(ns))
ms = []
for _ in range(N):
    ns = random.randint(3, 6); sl = [rslot(ns) for _ in range(2 * ns)]; sl[random.randrange(1, 2 * ns)] = '---'; sl[0] = '1R' + sl[0][2]
    ms.append('_'.join(sl[2*q] + sl[2*q+1] for q in range(ns)))
inp = ''.join(f'{m} A\n' for m in ms)
out = subprocess.run([SYM, 'run', '--tape', '--budget', '50000', '--sigwin', '0'], input=inp, capture_output=True, text=True).stdout.split('\n')
rows = []; i = 0
while i < len(out):
    if out[i].startswith('R '): rows.append((out[i].split(), out[i + 1])); i += 2
    else: i += 1
sel = [(f, t) for f, t in rows if int([x for x in f if x.startswith('aff=')][0][4:]) > 0]
print('machines', N, 'with affine applications', len(sel))
inp2 = ''.join(f'{f[1]} {f[2]}\n' for f, t in sel)
lo = subprocess.run([LIT, '300000000'], input=inp2, capture_output=True, text=True).stdout.split('\n')
L = []; i = 0
while i < len(lo):
    if lo[i].startswith('L '): L.append((lo[i].split(), lo[i + 1])); i += 2
    else: i += 1
C = collections.Counter(); bad = []
for (f, t), (l, lt) in zip(sel, L):
    sig = [x for x in f if x.startswith('sigma=')][0][6:]
    C[f'lit={l[3]} sym={f[3]}'] += 1
    if l[3] == 'HALT':
        if f[3] == 'CYCLE': bad.append(('UNSOUND', f[1]))
        elif f[3] == 'HALT' and (sig != l[5] or t != lt): bad.append(('mismatch', f[1], sig, l[5]))
        elif f[3] == 'HALT': C['halt match (affine used)'] += 1
for k, v in sorted(C.items()): print(f'{v:7d} {k}')
print('BAD', len(bad)); [print(' ', b) for b in bad[:20]]
