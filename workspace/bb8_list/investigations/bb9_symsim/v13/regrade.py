# regrade.py LIST OUT [BUDGET TLIMIT EXE] : v14 regrade from blank (real symbolic run, no substitution).
# LIST lines: machine [<TAB> template]  (template default: kg/fitted.tsv, else none).  symsim runs with all v13/v14
# accelerators (--canon --multi --dom; ITER/AFF/PKG on by default).  Output per machine: verdict, jumps, big clears
# (CDP with symbolic depth), symbolic ITER applications, sigma, last jumps.  Resumable.
import sys, os, subprocess, re
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lst, out = sys.argv[1], sys.argv[2]
bud = sys.argv[3] if len(sys.argv) > 3 else '1000000'; tl = sys.argv[4] if len(sys.argv) > 4 else '600'
exe = sys.argv[5] if len(sys.argv) > 5 else 'symsim_v14g.exe'; extra = sys.argv[6:]
fit = {}
for l in open(os.path.join(B, 'kg', 'fitted.tsv')):
    f = l.rstrip('\r\n').split('\t'); fit[f[0]] = f[3]
done = set(l.split()[0] for l in open(out)) if os.path.exists(out) else set()
fo = open(out, 'a')
for line in open(lst):
    f = line.rstrip('\r\n').split('\t'); m = f[0].strip()
    if not m or m in done: continue
    T = f[1].strip() if len(f) > 1 and f[1].strip() else fit.get(m, '')
    cmd = [os.path.join(B, exe), 'run', '--memcap', '2000', '--budget', bud, '--tlimit', tl, '--sigwin', '0', '--mg', '38918880', '--canon', '--multi', '--dom', '--rulecheck'] + extra
    if T: cmd += ['--tmpl', T]
    try:
        o = subprocess.run(cmd, input=f'{m} A\n', capture_output=True, text=True, timeout=int(float(tl)) + 600).stdout
    except subprocess.TimeoutExpired:
        fo.write(f'{m} TIMEOUT\n'); fo.flush(); continue
    R = [l for l in o.split('\n') if l.startswith('R ')]
    if not R: fo.write(f'{m} NOR\n'); fo.flush(); continue
    r = R[0]; p = r.split()
    def fld(k):
        x = [y for y in p if y.startswith(k + '=')]; return x[0][len(k) + 1:] if x else '?'
    jl = r.split('|')[1].strip() if '|' in r else ''
    fo.write(f'{m} {p[3]} {p[4]} {fld("rcu") and "rcu=" + fld("rcu")} kj={fld("kj")} bc={fld("bc")} sc={fld("sc")} it={fld("it")} its={fld("its")} aff={fld("aff")} macro={fld("macro")} sigma={fld("sigma")[:200]} | {jl[:600]}\n'); fo.flush()
