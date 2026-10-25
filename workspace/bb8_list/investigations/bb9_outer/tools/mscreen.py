# mscreen.py: single/double-slot mutant screen against synthetic test configurations (symsim v12, evidence only).
#   python mscreen.py BASE TEMPLATE TESTS OUT [LANE NLANES] [--pairs SLOTS_FILE]
# TESTS: file with lines "label<TAB>budget<TAB>maxjt<TAB>tape" (tape '-' = blank start).  For each mutant and test the
# canonical symsim output (JUMPTAPE tapes with symbols renamed by first appearance + the R verdict) is compared with the base.
# Row: mutant slot:new  then per test  label=SAME | label=D<j>:<verdict>  (j = index of first differing JUMPTAPE).
import sys, re, subprocess, os, itertools
D = os.path.dirname(os.path.abspath(__file__)); EXE = os.path.join(D, 'symsim_v12.exe')
args = [a for a in sys.argv[1:]]
pairs = None
if '--pairs' in args: i = args.index('--pairs'); pairs = args[i + 1]; del args[i:i + 2]
base, tmpl, tests_f, out = args[:4]; lane = int(args[4]) if len(args) > 4 else 0; nl = int(args[5]) if len(args) > 5 else 1
tests = [l.rstrip('\n').split('\t') for l in open(tests_f) if l.strip() and not l.startswith('#')]
def canon(txt, maxjt):
    names = {}
    def rn(m):
        k = m.group(0)
        if k not in names: names[k] = 'Y%d' % len(names)
        return names[k]
    jts = []; R = None
    for l in txt.split('\n'):
        if l.startswith('JUMPTAPE') and len(jts) < maxjt:
            tape, _, syms = l[9:].partition('   ')
            newest = re.findall(r'(X\d+)=([^\[]*)\[', syms)
            s = re.sub(r'X\d+', rn, tape)
            if newest: s += ' | ' + re.sub(r'X\d+', rn, newest[0][1])
            jts.append(s)
        elif l.startswith('R '):
            f = l.split(); v = f[3]; sg = [x for x in f if x.startswith('sigma=')]
            R = v + ' ' + (re.sub(r'X\d+', rn, sg[0]) if sg else '')
    return jts, R
def run(m, t):
    lab, bud, maxjt, tape = t
    inp = f'{m} A\n' if tape == '-' else f'{m} A {tape}\n'
    try:
        o = subprocess.run([EXE, 'run', '--tmpl', tmpl, '--jumpdump', '--budget', bud, '--tlimit', '15', '--sigwin', '0', '--mg', '38918880', '--memcap', '800'],
                           input=inp, capture_output=True, text=True, timeout=40).stdout
    except subprocess.TimeoutExpired: return [], 'TIMEOUT'
    rul = 'UNRULED' if 'UNRULED' in o else ''
    j, R = canon(o, int(maxjt))
    return j, (R or 'NOR') + (' ' + rul if rul else '')
TR = ['---'] + [f'{w}{d}{chr(65 + s)}' for s in range(9) for w in '01' for d in 'LR']
slots = [(q, c) for q in range(9) for c in range(2)]
def mut(m, changes):
    rows = m.split('_')
    for (q, c), v in changes: rows[q] = rows[q][:3 * c] + v + rows[q][3 * c + 3:]
    return '_'.join(rows)
def get(m, q, c): return m.split('_')[q][3 * c:3 * c + 3]
ref = {t[0]: run(base, t) for t in tests}
done = set(l.split()[0] for l in open(out)) if os.path.exists(out) else set()
fo = open(out, 'a')
if pairs is None:
    cands = [((s, v),) for s in slots for v in TR if v != get(base, *s)]
else:
    ps = [tuple(x.split(':')) for x in open(pairs).read().split()]   # "E0:1RB" style first changes
    cands = []
    for p in ps:
        s1 = (ord(p[0][0]) - 65, int(p[0][1]));
        for s in slots:
            if s == s1: continue
            for v in TR:
                if v != get(base, *s): cands.append(((s1, p[1]), (s, v)))
for idx, ch in enumerate(cands):
    if idx % nl != lane: continue
    m = mut(base, ch)
    if m in done: continue
    if m.count('---') == 0: continue     # keep at least one halt
    res = []
    for t in tests:
        j, R = run(m, t); rj, rR = ref[t[0]]
        if j == rj and R == rR: res.append(f'{t[0]}=SAME'); continue
        k = next((i for i in range(min(len(j), len(rj))) if j[i] != rj[i]), min(len(j), len(rj)))
        res.append(f'{t[0]}=D{k}:{R.replace(" ", "_")}')
        if t[0] == 'quick' and k == 0: break
    lab = ','.join(f'{chr(65 + s[0])}{s[1]}:{v}' for s, v in ch)
    fo.write(f'{m} {lab} ' + ' '.join(res) + '\n'); fo.flush()
