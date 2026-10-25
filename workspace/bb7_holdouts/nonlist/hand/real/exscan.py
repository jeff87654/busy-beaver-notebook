"""exscan.py MACHINE K TEMPLATE MAXMACRO VAR=range [VAR=range ...] [--g=5] [--sep=00] [--extra=M]
Runs ms.exe (exact) from TEMPLATE.format(**vars) for every combination; for each: HALT (macro, steps, ones) or the
group view (split at SEP blocks, left-end events) at the first left-end event with >= g groups ('rebuild'), then
continues EXTRA more macro steps checking for a halt. Prints one line per combination. range = a-b or a-b:step or list a,b,c."""
import subprocess, sys, itertools, re
args = [a for a in sys.argv[1:] if not a.startswith('--')]
opts = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--') and '=' in a)
m, K, tp, mm = args[:4]; G = int(opts.get('g', '5')); SEP = opts.get('sep', '00'); EX = int(opts.get('extra', '0'))
MS = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
def rng(s):
    if ',' in s: return [int(x) for x in s.split(',')]
    st = 1
    if ':' in s: s, st = s.split(':'); st = int(st)
    a, b = s.split('-'); return range(int(a), int(b) + 1, st)
vs = [(a.split('=')[0], rng(a.split('=')[1])) for a in args[4:]]
def groups(t):
    gs = [[]]
    for x in t:
        s, n = (x.split('^') + ['1'])[:2]
        if s == SEP:
            for _ in range(int(n)): gs.append([])
        else: gs[-1].append(s if n == '1' else s + '^' + n)
    gs = ['.'.join(g) if g else '-' for g in gs]
    out = []; i = 0
    while i < len(gs):
        j = i
        while j + 1 < len(gs) and gs[j + 1] == gs[i]: j += 1
        out.append(gs[i] if j == i else f'[{gs[i]}]x{j-i+1}'); i = j + 1
    return gs, ' | '.join(out)
for combo in itertools.product(*[v for _, v in vs]):
    d = dict(zip([k for k, _ in vs], combo))
    p = subprocess.Popen([MS, m, K, mm, 'l0', 'i'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, creationflags=0x40)
    p.stdin.write(tp.format(**d) + '\n'); p.stdin.close()
    res = 'END'; reb = None; rebit = None
    for l in p.stdout:
        if l.startswith('H'): res = 'HALT ' + l.strip()[2:]; break
        if not l.startswith('T'): 
            if l.startswith('INBLOCK'): res = 'INBLOCK'
            continue
        a, s = l.split('|', 1); t = s.split()
        if not t or not t[0].startswith('['): continue
        if reb is None:
            ng = 1 + sum(int((x.split('^') + ['1'])[1]) for x in t[1:] if x.split('^')[0] == SEP)
            if ng >= G:
                gs, c = groups(t[1:])
                reb = c; rebit = int(a.split()[1])
                if EX == 0: break
        elif int(a.split()[1]) > rebit + EX: break
    p.kill()
    print(' '.join(f'{k}={v}' for k, v in d.items()), res if res != 'END' or reb is None else 'REB', (reb or '')[:160], flush=True)
