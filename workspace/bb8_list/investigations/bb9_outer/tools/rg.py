# rg.py: round grader for L1-form machines (evidence only).  Runs symsim from blank (or a given tape); whenever a JUMPTAPE
# has the L1 round form
#     <left> 1^2 (010101011)^{N} 0 1^2 (011)^k (01)^{3*Xb} 1 0 1 0 1 0 1 G>       (or the equal 1 (101010101)^N 1 0 1^2 form)
# with a symbolic counter N = 12*Xa+c, the round is fast-forwarded to N = NFF (default 5) with k += N - NFF, every symbol
# replaced by an order-faithful representative  r + MG*t  (r = symsim residue mod MG, t grows by x FAC per round so that
# X_current >> k >> X_previous).  Then symsim continues.  Reports per machine: rounds done, final verdict, sigma, left part.
#   python rg.py LIST OUT TEMPLATE [ROUNDS] [BUDGET]      LIST lines: machine [tape]
import sys, re, subprocess, os
D = os.path.dirname(os.path.abspath(__file__)); EXE = os.path.join(D, 'symsim_v12.exe')
MG = 38918880; NFF = 5; FAC = 40
RXs = [re.compile(r'^(.*?)1\^2 010101011\^\{12\*X(\d+)([+-]\d+)\} 0 1\^2 011\^(\d+) 01\^\{3\*X(\d+)\} 1 0 1 0 1 0 1 G>$'),
       re.compile(r'^(.*?)1 101010101\^\{12\*X(\d+)([+-]\d+)\} 1 0 1\^2 011\^(\d+) 01\^\{3\*X(\d+)\} 1 0 1 0 1 0 1 G>$')]
def symsim(m, tape, tmpl, bud):
    inp = f'{m} A {tape}\n' if tape else f'{m} A\n'
    try:
        return subprocess.run([EXE, 'run', '--tmpl', tmpl, '--jumpdump', '--budget', str(bud), '--tlimit', '60', '--sigwin', '0', '--mg', str(MG), '--memcap', '1000'],
                              input=inp, capture_output=True, text=True, timeout=200).stdout
    except subprocess.TimeoutExpired: return 'TIMEOUT'
def grade(m, tape0, tmpl, rounds, bud):
    tape = tape0; t = 1; log = []; lastXa = None
    for rd in range(rounds + 1):
        o = symsim(m, tape, tmpl, bud)
        if o == 'TIMEOUT': log.append('TIMEOUT'); return log
        ff = None
        for l in o.split('\n'):
            if not l.startswith('JUMPTAPE'): continue
            tp, _, syms = l[9:].partition('   ')
            for RX in RXs:
                g = RX.match(tp.strip())
                if g: break
            else: continue
            res = dict((k, int(v)) for k, v in re.findall(r'X(\d+)=[^\[]*\[r(\d+)\]', syms))
            if g.group(2) == lastXa or g.group(2) not in res or g.group(5) not in res: continue
            ff = (g, res); break
        R = [l for l in o.split('\n') if l.startswith('R ')]
        if ff is None:
            v = R[0].split()[3] if R else 'NOR'
            sg = [x for x in R[0].split() if x.startswith('sigma=')][0] if R else ''
            kj = [x for x in R[0].split() if x.startswith('kj=')][0] if R else ''
            log.append(f'END {v} {kj} {sg}' + (' UNRULED' if 'UNRULED' in o else ''))
            return log
        g, res = ff; left = g.group(1); lastXa = None
        xa = res[g.group(2)] + MG * t; N = 12 * xa + int(g.group(3)); k = int(g.group(4)) + N - NFF
        t2 = t * FAC; xb = res[g.group(5)] + MG * t2
        while xb <= 4 * k: t2 *= FAC; xb = res[g.group(5)] + MG * t2
        t = t2
        log.append(f'R{rd} left="{left.strip()}" N=12*X+{g.group(3)} k->{k}')
        tape = f'{left}1^2 010101011^{NFF} 0 1^2 011^{k} 01^{3 * xb} 1 0 1 0 1 0 1 G>'
    log.append('ROUNDS-DONE'); return log
if __name__ == '__main__':
    lst, out, tmpl = sys.argv[1:4]; rounds = int(sys.argv[4]) if len(sys.argv) > 4 else 4; bud = int(sys.argv[5]) if len(sys.argv) > 5 else 6000
    done = set(l.split()[0] for l in open(out)) if os.path.exists(out) else set()
    fo = open(out, 'a')
    for line in open(lst):
        p = line.split(None, 1)
        if not p or p[0] in done: continue
        log = grade(p[0], p[1].strip() if len(p) > 1 else '', tmpl, rounds, bud)
        fo.write(p[0] + ' | ' + ' || '.join(log) + '\n'); fo.flush()
