# exprobe.py MACHINE [BUDGET0 BUDGET1 EXE] : counter-exhaustion probe for counter loops (evidence only, not a proof).
# 1. run symsim from blank (template from kg/fitted.tsv) for BUDGET0 macro steps and take the final tape;
# 2. the counter = the run whose count has the largest coefficient on the first clear X0 (12*X0 + c type);
# 3. rebuild the tape with that count := 0, 1, 2 and every other symbolic count := a fresh HUGE symbol (^H) carrying the
#    true residue mod 38918880 (lower bound 10^6), and run symsim again (BUDGET1) from each probe tape.
# Prints the verdict of each probe: HALT (with its jump log) means the exhaustion branch reaches a halt.
import sys, re, subprocess, os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = sys.argv[1].strip(); b0 = sys.argv[2] if len(sys.argv) > 2 else '20000'; b1 = sys.argv[3] if len(sys.argv) > 3 else '100000'
exe = sys.argv[4] if len(sys.argv) > 4 else 'symsim_v14d.exe'; MG = 38918880
T = ''
for l in open(os.path.join(B, 'kg', 'fitted.tsv')):
    f = l.rstrip('\r\n').split('\t')
    if f[0] == m: T = f[3]
opts = ['--memcap', '2000', '--sigwin', '0', '--mg', str(MG), '--canon', '--multi', '--dom'] + (['--tmpl', T] if T else [])
r = subprocess.run([os.path.join(B, exe), 'run', '--budget', b0, '--tlimit', '200', '--tape', '--tapeall', '400'] + opts, input=f'{m} A\n', capture_output=True, text=True).stdout.split('\n')
tape = [l for l in r if l.startswith('TAPE ')]; syms = [l for l in r if l.startswith('TAPESYMS')]
if not tape: print(m, 'NOTAPE'); sys.exit()
tape = tape[0][5:]; syms = syms[0] if syms else ''
if tape.startswith('...'): print(m, 'TAPE-TRUNCATED'); sys.exit()
res = {k: int(v) for k, v in re.findall(r'X(\d+)=[^\[]*\[r(\d+)\]', syms)}
def lin_res(e):   # residue mod MG of a Lin string like 12*X0+35 or (2*X3+1)/3 (division: give up)
    if '/' in e: return None
    tot = 0
    for sign, coef, var, const in re.findall(r'([+-]?)(?:(\d+)\*)?(?:X(\d+)|(\d+))', e):
        sg = -1 if sign == '-' else 1
        if var:
            if var not in res: return None
            tot += sg * (int(coef) if coef else 1) * res[var]
        elif const: tot += sg * int(const)
    return tot % MG
toks = tape.split()
# counter: symbolic count with the largest coefficient on the lowest-numbered symbol (the first clear)
best, bi = -1, -1
for i, t in enumerate(toks):
    mm = re.match(r'([01]+)\^\{(.*)\}$', t)
    if not mm: continue
    cm = re.search(r'(\d+)\*X0(?!\d)', mm.group(2))
    c = int(cm.group(1)) if cm else (1 if re.search(r'(^|[+])X0(?!\d)', mm.group(2)) else 0)
    if c > best: best, bi = c, i
if bi < 0 or best < 2: print(m, 'NOCOUNTER', tape[:200]); sys.exit()
out = []
for cval in (0, 1, 2):
    nt = []
    for i, t in enumerate(toks):
        mm = re.match(r'([01]+)\^\{(.*)\}$', t)
        if i == bi: nt.append(f'{mm.group(1)}^{cval}' if cval > 0 else ''); continue
        if mm:
            rr = lin_res(mm.group(2))
            if rr is None: nt = None; break
            nt.append(f'{mm.group(1)}^H{rr}')
        else:
            nt.append(t)
    if nt is None: out.append(f'c={cval}:NORES'); continue
    spec = ' '.join(x for x in nt if x)
    # initTape only knows Q> for the head; turn "<Q" into a head on the left neighbour cell
    if re.search(r'<[A-P]', spec):
        parts = spec.split(); j = [k for k, x in enumerate(parts) if re.fullmatch(r'<[A-P]', x)][0]
        q = parts[j][1]; left = parts[:j]
        lw = left[-1]; w, _, cnt = lw.partition('^')
        if cnt and cnt.startswith('H'): out.append(f'c={cval}:HEADSYM'); continue
        n = int(cnt) if cnt else 1
        cells = w * n
        left = left[:-1] + ([cells[:-1]] if len(cells) > 1 else [])
        spec = ' '.join(left + [q + '>', cells[-1]] + parts[j + 1:])
    o = subprocess.run([os.path.join(B, exe), 'run', '--budget', b1, '--tlimit', '200', '--hlb', '1000000'] + opts, input=f'{m} A {spec}\n', capture_output=True, text=True).stdout
    R = [l for l in o.split('\n') if l.startswith('R ')]
    if not R: out.append(f'c={cval}:NOR'); continue
    p = R[0].split(); jl = R[0].split('|')[1].strip() if '|' in R[0] else ''
    kj = [x for x in p if x.startswith('kj=')]
    out.append(f'c={cval}:{p[3]}:{kj[0] if kj else ""}' + f'[{jl[:100]}]')
print(m, 'counter', toks[bi], '|', ' '.join(out))
