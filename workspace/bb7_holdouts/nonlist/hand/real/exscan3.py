"""exscan3.py MACHINE K TEMPLATE MAXMACRO_EXPR RUNS EXTRA_EXPR VAR=range ... [--sep=00] [--full] [--to=SEC]
ms3.exe (exact, silent): from TEMPLATE.format(vars) run until the tape has >= RUNS runs, then EXTRA_EXPR (python expr
in the vars) more macro steps (total cap MAXMACRO_EXPR); print HALT line, or the final tape as groups (split at SEP),
list repeats compressed, plus a count-free skeleton. range: a-b, a-b:step or a,b,c. Logs own PID to nonlist/pids.txt;
children are only killed through subprocess timeout."""
import subprocess, sys, itertools, re, os, time
args = [a for a in sys.argv[1:] if not a.startswith('--')]
opts = dict((a[2:].split('=', 1) + [''])[:2] for a in sys.argv[1:] if a.startswith('--'))
m, K, tp, mm, RUNS, EXE = args[:6]; SEP = opts.get('sep', '00'); TO = float(opts.get('to', '60'))
MS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ms3.exe')
PIDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'pids.txt')
open(PIDS, 'a').write(f'{os.getpid()}\t{time.strftime("%Y-%m-%d %H:%M:%S")}\tpython exscan3.py {m} (tier1-real agent)\n')
def rng(s):
    if ',' in s: return [int(x) for x in s.split(',')]
    st = 1
    if ':' in s: s, st = s.split(':'); st = int(st)
    a, b = s.split('-'); return range(int(a), int(b) + 1, st)
vs = [(a.split('=')[0], rng(a.split('=')[1])) for a in args[6:]]
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
    return ' | '.join(out)
for combo in itertools.product(*[v for _, v in vs]):
    d = dict(zip([k for k, _ in vs], combo)); tag = ' '.join(f'{k}={v}' for k, v in d.items())
    ex = int(eval(EXE, {}, d)); mx = int(eval(mm, {}, d))
    try:
        r = subprocess.run([MS, m, K, str(mx), 's' + RUNS, 'i', str(ex)], input=tp.format(**d) + '\n', capture_output=True,
                           text=True, creationflags=0x40, timeout=TO).stdout.strip()
    except subprocess.TimeoutExpired:
        print(tag, 'TIMEOUT', flush=True); continue
    if r.startswith('H'): print(tag, 'HALT', r[2:], flush=True); continue
    if not r.startswith('R'): print(tag, 'NOTRIG', r[:100], flush=True); continue
    a, s = r.split('|', 1); t = s.split()
    g = groups(t); sk = re.sub(r'\^\d+', '^n', re.sub(r'x\d+', 'xM', g))
    print(tag, 'CONT', a.split()[1], a.split()[5], a.split()[6], '::', g[:150] if 'full' not in opts else g, '::', sk[:150], flush=True)
