"""Check the TM layer of zfc_254:  halts tm c0 <-> rm_halts p254 ([], R0).

1. the input files have the expected hashes;
2. coq/Table254.v is exactly the transition table of inputs/zfc_254.tm (independent parse of both);
3. coq/Table254.v and coq/Prog254.v are reproduced byte for byte by tools/gen_table.py / gen_prog.py;
4. a clean rebuild of coq/Main.v (coqc 8.20, Idle priority) succeeds;
5. the statements of tm254_rm / tm254_iter are the expected ones and Print Assumptions reports
   no axioms.

Usage: python check_tm254.py   (from any directory)"""
import hashlib, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
INP = HERE.parent / 'inputs'
COQ = HERE / 'coq'
TOOLS = HERE / 'tools'
EXPECT = {
    'zfc_254.tm': 'd655ce2cf8cccebd21caa21a49f0f9f010960a44b95c17aae6cc425c518954eb',
}


def fail(msg):
    print('FAIL:', msg)
    sys.exit(1)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


# 1. hashes
for name, h in EXPECT.items():
    if sha(INP / name) != h:
        fail(f'{name} hash mismatch')
print('inputs: zfc_254.tm sha256 ok; paths.json sha256', sha(INP / 'paths.json'))

# 2. independent comparison of the table
rows = {}
for line in (INP / 'zfc_254.tm').read_text().splitlines():
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    s, r, w, d, n = line.split()
    rows[(int(s), int(r))] = (int(w), d, int(n))
text = (COQ / 'Table254.v').read_text()
body = text[text.index('Definition table254'):]
tup = re.findall(r'\((true|false), ([LR]), (\d+), (true|false), ([LR]), (\d+)\)', body)
if len(tup) != 254:
    fail(f'Table254.v has {len(tup)} rows')
for q, (w0, d0, n0, w1, d1, n1) in enumerate(tup):
    if rows[(q, 0)] != (int(w0 == 'true'), d0, int(n0)) or rows[(q, 1)] != (int(w1 == 'true'), d1, int(n1)):
        fail(f'row {q} differs')
if len(rows) != 2 * 254 or any(q >= 254 for q, _ in rows):
    fail('the file has rows outside states 0..253')
print('Table254.v = zfc_254.tm (254 states x 2 symbols; state 254 has no row)')

# 3. generated files are reproducible
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    for gen, args, out in [('gen_table.py', [INP / 'zfc_254.tm'], 'Table254.v'),
                           ('gen_prog.py', [INP / 'paths.json'], 'Prog254.v')]:
        r = subprocess.run([sys.executable, '-I', str(TOOLS / gen), *map(str, args), str(td / out)],
                           capture_output=True, text=True)
        if r.returncode or (td / out).read_bytes() != (COQ / out).read_bytes():
            fail(f'{out} is not reproduced by {gen}\n{r.stdout}{r.stderr}')
print('Table254.v and Prog254.v reproduced by the generators')

# 4. clean rebuild
for f in COQ.glob('*.vo*'):
    f.unlink()
r = subprocess.run([sys.executable, str(COQ / 'build.py'), 'Main.v'], capture_output=True, text=True)
print(r.stdout)
if r.returncode:
    fail('build failed\n' + r.stderr)

# 5. statements and assumptions
main = (COQ / 'Main.v').read_text()
for stmt in ['Theorem tm254_rm : halts tm c0 <-> rm_halts p254 ([], R0).',
             'Corollary tm254_iter : halts tm c0 <-> iter_halts p254 R0.']:
    if stmt not in main:
        fail('statement changed: ' + stmt)
prog = (COQ / 'Prog254.v').read_text()
if 'Definition R0 : regs := upd regs0 0 2.' not in prog:
    fail('R0 changed')
out_main = r.stdout[r.stdout.index('compiled Main.v'):]
if out_main.count('Closed under the global context') != 2 or 'Axioms' in out_main:
    fail('assumptions not closed')
print('PASS: tm254_rm and tm254_iter proved, closed under the global context')
