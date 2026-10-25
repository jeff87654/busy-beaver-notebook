# faith.py MACHINE [BUDGET TLIMIT REP EXE extra...] : run symsim from the first post-clear tape with every symbol X := its residue r
# mod 38918880 (REP=full: X := r; REP=k: X := r + k*38918880), i.e. an order-faithful exact world.  Prints the R/TAPE lines.
import sys, re, subprocess, os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = sys.argv[1].strip(); bud = sys.argv[2] if len(sys.argv) > 2 else '200000'; tl = sys.argv[3] if len(sys.argv) > 3 else '120'
k = int(sys.argv[4]) if len(sys.argv) > 4 else 0; exe = sys.argv[5] if len(sys.argv) > 5 else 'symsim_v12.exe'; extra = sys.argv[6:]
T = [l.rstrip('\n').split('\t')[3] for l in open(os.path.join(B, 'kg', 'fitted.tsv')) if l.split('\t')[0] == m][0]
r = subprocess.run([os.path.join(B, 'symsim_v12.exe'), 'run', '--memcap', '1500', '--tmpl', T, '--jumpstop', '--budget', '100000', '--tlimit', '900', '--sigwin', '0', '--mg', '38918880'],
                   input=f'{m} A\n', capture_output=True, text=True).stdout
jt = [l for l in r.split('\n') if l.startswith('JUMPTAPE')][0][9:]
tape, _, syms = jt.partition('  ')
res = {kk: int(v) + k * 38918880 for kk, v in re.findall(r'X(\d+)=[^\[]*\[r(\d+)\]', syms)}
def ev(g):
    e = g.group(1)
    for kk in sorted(res, key=lambda z: -len(z)): e = re.sub(r'X' + kk + r'(?!\d)', str(res[kk]), e)
    return str(eval(e.replace('/', '//')))
s = re.sub(r'\{([^}]*)\}', ev, tape)
print('START', s[:300], file=sys.stderr)
o = subprocess.run([os.path.join(B, exe), 'run', '--memcap', '1500', '--tmpl', T, '--tapeall', '60', '--budget', bud, '--tlimit', tl, '--sigwin', '0', '--mg', '38918880'] + extra,
                   input=f'{m} A {s}\n', capture_output=True, text=True)
print(o.stdout); sys.stderr.write(o.stderr)
