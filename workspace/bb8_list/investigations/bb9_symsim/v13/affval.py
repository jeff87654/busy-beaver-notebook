# affval.py LIST NMAX OUT [LITBUDGET SYMEXE] : validation of v13 affine / ITER acceleration against literal runs.
# For each machine: post-clear tape (symsim v12 --jumpstop), every symbol X := n for n = 1..NMAX (small, NOT residue-faithful:
# these are just test inputs), then lit and symsim (template + AFF/ITER on) from the same exact tape.
# Every literal HALT must be a symsim HALT with the same sigma and tape; a symsim CYCLE must never halt literally.
import sys, re, subprocess, os, collections
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lst, nmax, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
litb = sys.argv[4] if len(sys.argv) > 4 else '200000000'; exe = sys.argv[5] if len(sys.argv) > 5 else 'symsim_v13d.exe'
tm = {l.split('\t')[0]: l.rstrip('\n').split('\t')[3] for l in open(os.path.join(B, 'kg', 'fitted.tsv'))}
done = set(l.split()[0] for l in open(out)) if os.path.exists(out) else set()
fo = open(out, 'a')
for m in [l.split()[0] for l in open(lst)]:
    if m in done: continue
    T = tm[m]
    r = subprocess.run([os.path.join(B, 'symsim_v12.exe'), 'run', '--memcap', '1500', '--tmpl', T, '--jumpstop', '--budget', '100000', '--tlimit', '60', '--sigwin', '0', '--mg', '38918880'],
                       input=f'{m} A\n', capture_output=True, text=True).stdout
    jt = [l for l in r.split('\n') if l.startswith('JUMPTAPE')]
    if not jt: fo.write(f'{m} NOJUMP\n'); fo.flush(); continue
    tape = jt[0][9:].partition('  ')[0]
    specs = []
    for n in range(1, nmax + 1):
        def ev(g):
            e = re.sub(r'X\d+', str(n), g.group(1)); v = eval(e.replace('/', '//'))
            return str(max(v, 0))
        specs.append(re.sub(r'\{([^}]*)\}', ev, tape).replace('^0 ', ' ').replace('^0', ''))
    inp = ''.join(f'{m} A {s}\n' for s in specs)
    lo = subprocess.run([os.path.join(B, 'lit.exe'), litb], input=inp, capture_output=True, text=True).stdout.split('\n')
    so = subprocess.run([os.path.join(B, exe), 'run', '--memcap', '1500', '--tmpl', T, '--tape', '--budget', '300000', '--tlimit', '30', '--sigwin', '0', '--mg', '38918880'],
                        input=inp, capture_output=True, text=True).stdout.split('\n')
    L = []; i = 0
    while i < len(lo):
        if lo[i].startswith('L '): L.append((lo[i].split(), lo[i + 1] if i + 1 < len(lo) else '')); i += 2
        else: i += 1
    S = []; i = 0
    while i < len(so):
        if so[i].startswith('R '): S.append((so[i].split(), so[i + 1] if i + 1 < len(so) else '')); i += 2
        else: i += 1
    C = collections.Counter(); bad = []
    for n, (l, lt), (s, st) in zip(range(1, nmax + 1), L, S):
        sig = [x for x in s if x.startswith('sigma=')][0][6:]
        aff = int([x for x in s if x.startswith('aff=')][0][4:]); it = int([x for x in s if x.startswith('it=')][0][3:]) if any(x.startswith('it=') for x in s) else 0
        tag = ('A' if aff else '') + ('I' if it else '')
        C[f'{l[3]}/{s[3]}{"+" + tag if tag else ""}'] += 1
        if l[3] == 'HALT':
            if s[3] == 'CYCLE': bad.append(f'UNSOUND n={n}')
            elif s[3] == 'HALT' and (sig != l[5] or st != lt): bad.append(f'MISMATCH n={n} {sig} {l[5]}')
    fo.write(f'{m} ' + ' '.join(f'{k}:{v}' for k, v in sorted(C.items())) + (' BAD ' + ';'.join(bad) if bad else '') + '\n'); fo.flush()
