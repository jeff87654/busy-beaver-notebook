# pexp.py: prefix explorer.  For each binary prefix P (placed left of the round-end tape SEND), run symsim and report
# what the restart does with P:  HALT | ROUND P'=<cells left of the new round's counter> cnt=<counter expr> | OTHER | BUDGET.
#   python pexp.py MACHINE TEMPLATE SEND MAXLEN OUT [BUDGET]
# A new round is recognised by the JUMPTAPE form  <left> 010101011^{12*Xa+c} 011^3 01^{3*Xb} 1 0 1 0 1 0 1 G>.
import sys, re, subprocess, os, itertools
D = os.path.dirname(os.path.abspath(__file__)); EXE = os.path.join(D, 'symsim_v12.exe')
m, tmpl, send, maxlen, out = sys.argv[1:6]; bud = sys.argv[6] if len(sys.argv) > 6 else '3000'
RX = re.compile(r'^(.*?)010101011\^\{12\*X\d+\+(\d+)\} 011\^3 01\^\{3\*X\d+\} 1 0 1 0 1 0 1 G>$')
def expand(s):
    o = ''
    for t in s.split():
        w, _, e = t.partition('^')
        o += w * (int(e) if e else 1)
    return o
def tok(P):   # cells string -> symsim tokens
    return ' '.join(P)
def run(P):
    inp = f'{m} A {tok(P)} {send}\n' if P else f'{m} A {send}\n'
    try:
        o = subprocess.run([EXE, 'run', '--tmpl', tmpl, '--jumpdump', '--budget', bud, '--tlimit', '40', '--sigwin', '0', '--mg', '38918880', '--memcap', '800'],
                           input=inp, capture_output=True, text=True, timeout=120).stdout
    except subprocess.TimeoutExpired: return 'TIMEOUT'
    first = None
    for l in o.split('\n'):
        if l.startswith('JUMPTAPE'):
            tape = l[9:].partition('   ')[0].strip()
            g = RX.match(tape)
            if g:
                try: left = expand(g.group(1))
                except ValueError: left = '?' + g.group(1)
                return f'ROUND P\'={left.lstrip("0") or "-"} c={g.group(2)}'
            if first is None: first = tape
    R = [l for l in o.split('\n') if l.startswith('R ')]
    v = R[0].split()[3] if R else 'NOR'
    sg = [x for x in R[0].split() if x.startswith('sigma=')][0] if R else ''
    mac = [x for x in R[0].split() if x.startswith('macro=')][0] if R else ''
    if v == 'HALT': return f'HALT {mac} {sg}'
    return f'{v} first={first[:150] if first else "-"}'
done = set(l.split()[0] for l in open(out)) if os.path.exists(out) else set()
fo = open(out, 'a')
Ps = ['']
for L in range(1, int(maxlen) + 1):
    for bits in itertools.product('01', repeat=L - 1): Ps.append('1' + ''.join(bits))
for P in Ps:
    key = P or '-'
    if key in done: continue
    fo.write(f'{key} {run(P)}\n'); fo.flush()
