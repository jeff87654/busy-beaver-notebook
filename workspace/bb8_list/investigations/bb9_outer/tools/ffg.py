# ffg.py: generic order-faithful round grader with counter fast-forward (evidence only; symsim v12 engine).
#   python ffg.py LIST OUT [ROUNDS BUDGET]     LIST lines: machine<TAB>template   (template = symsim --tmpl string)
# Segment loop: run symsim --jumpdump from the current tape (blank at first).  Scan its JUMPTAPE lines; when 3 consecutive
# ones share a skeleton (words, symbolic parts; the per-jump fresh symbol renamed F) and their numeric constants move by a
# constant per-jump delta with some constant decreasing and > CMIN (a counter), fast-forward:
#   - every symbol is replaced by an order-faithful representative r + MG*t (r = symsim residue), older symbols smaller,
#     the fresh symbol much larger than every resulting exponent;
#   - n jumps are skipped, n a multiple of 2520 (all exponents keep their residues mod 2520), leaving the counter < CMIN+2520.
# A segment that ends HALT/CYCLE/BUDGET without a counter ends the grade.  Rounds = number of fast-forwards on DIFFERENT
# skeleton/counter-symbol instances (each fresh counter = one round).
import sys, re, subprocess, os, time
D = os.path.dirname(os.path.abspath(__file__)); EXE = os.path.join(D, 'symsim_v12.exe')
MG = 38918880; RM = int(os.environ.get("FFM", "38918880")); P = int(os.environ.get("FFP", "360")); CMIN = 5; NSUB = 3
TOK = re.compile(r'(\S+?)\^(\{[^}]*\}|\d+)|(\S+)')
def parse(tape):
    out = []
    for m in TOK.finditer(tape):
        if m.group(3) is not None: out.append((m.group(3), None)); continue
        e = m.group(2)
        out.append((m.group(1), e[1:-1] if e.startswith('{') else e))
    return out
def lin(e):   # exponent -> (dict sym->coef, const) ; None if non-affine
    if e is None: return ({}, 1)
    e = e.replace(' ', '')
    if re.fullmatch(r'\d+', e): return ({}, int(e))
    terms = re.findall(r'([+-]?)(\d*)\*?(X\d+)?', e)
    co = {}; c = 0; pos = 0
    for sg, num, x in terms:
        if not num and not x: continue
        v = int(num) if num else 1
        if sg == '-': v = -v
        if x: co[x] = co.get(x, 0) + v
        else: c += v
    # verify reconstruct
    if not re.fullmatch(r'([+-]?(\d+\*)?X\d+|[+-]?\d+)+', e): return None
    return (co, c)
def skel(jt, fresh):
    sk = []; cs = []
    for w, e in parse(jt):
        L = lin(e)
        if L is None: return None, None
        co, c = L
        sk.append((w, tuple(sorted(('F' if x in fresh else x, v) for x, v in co.items()))))
        cs.append(c)
    return tuple(sk), cs
def symsim(m, tape, tmpl, bud):
    inp = f'{m} A {tape}\n' if tape else f'{m} A\n'
    try:
        return subprocess.run([EXE, 'run', '--tmpl', tmpl, '--jumpdump', '--budget', str(bud), '--tlimit', os.environ.get('FFT', '20'), '--sigwin', '0', '--mg', str(MG), '--memcap', '1000'],
                              input=inp, capture_output=True, text=True, timeout=200).stdout
    except subprocess.TimeoutExpired: return 'TIMEOUT'
def grade(m, tmpl, rounds, bud, tape0=''):
    tape = tape0; log = []; tgen = 1; nsub = 0; nff = 0
    t0 = time.time(); TCAP = float(os.environ.get('FFCAP', '120'))
    while nff <= rounds:
        if time.time() - t0 > TCAP: log.append('TCAP'); break
        o = symsim(m, tape, tmpl, bud)
        if o == 'TIMEOUT': log.append('TIMEOUT'); break
        jts = []
        for l in o.split('\n'):
            if l.startswith('JUMPTAPE'):
                tp, _, syms = l[9:].partition('   ')
                res = dict(('X' + k, int(v)) for k, v in re.findall(r'X(\d+)=[^\[]*\[r(\d+)\]', syms))
                jts.append((tp.strip(), res))
        ff = None
        for i in range(2, len(jts)):
            a, b, c = jts[i - 2], jts[i - 1], jts[i]
            sa = set(re.findall(r'X\d+', a[0])); sb = set(re.findall(r'X\d+', b[0])); sc = set(re.findall(r'X\d+', c[0]))
            ka, ca = skel(a[0], sa - sb); kb, cb = skel(b[0], sb - sa); kc, cc = skel(c[0], sc - sb)
            if ka is None or kb is None or kc is None: continue
            if not (ka == kb == kc): continue
            d = [y - x for x, y in zip(cb, cc)]
            if [y - x for x, y in zip(ca, cb)] != d or not any(v < 0 for v in d): continue
            fr = sc - sb; st = sc - fr
            if any(x not in c[1] for x in sc): continue
            rep0 = dict((x, c[1][x] % RM + RM * tgen) for x in st)
            vals = [cv + sum(v * rep0[x] for x, v in lin(e)[0].items() if x in rep0) for (w, e), cv in zip(parse(c[0]), cc)]
            if any(x in fr for (w, e), dd in zip(parse(c[0]), d) if dd < 0 for x in lin(e)[0]): continue
            ci = [j for j, v in enumerate(d) if v < 0]
            n = min((vals[j] - CMIN) // (-d[j]) for j in ci)
            n = (n // P) * P
            if n <= 0: continue
            ff = (c, d, n, fr); break
        R = [l for l in o.split('\n') if l.startswith('R ')]
        if ff is None:
            v = R[0].split()[3] if R else 'NOR'
            sg = [x for x in R[0].split() if x.startswith('sigma=')][0] if R else ''
            kj = [x for x in R[0].split() if x.startswith('kj=')][0] if R else ''
            if v == 'BUDGET' and jts and nsub < NSUB:
                # re-substitute the last jump tape (symbols -> order-faithful numbers by creation index) and go on
                tp, res = jts[-1]; syms_ = sorted(set(re.findall(r'X\d+', tp)), key=lambda x: int(x[1:]))
                if all(x in res for x in syms_):
                    rep = {}; t = tgen
                    cmax = max([lin(e)[1] for w, e in parse(tp) if lin(e) is not None] + [1])
                    for x in syms_:
                        while res[x] % RM + RM * t <= 2 * cmax: t *= 2
                        rep[x] = res[x] % RM + RM * t; cmax = max(cmax, 12 * rep[x]); t *= 4
                    parts = []; ok = True
                    for w, e in parse(tp):
                        L = lin(e)
                        if L is None: ok = False; break
                        val = L[1] + sum(cv * rep[x] for x, cv in L[0].items())
                        if val < 0: ok = False; break
                        if val: parts.append(w if val == 1 and e is None else f'{w}^{val}')
                    if ok:
                        nsub += 1; tgen = t; tape = ' '.join(parts); log.append(f'SUB{nsub}({kj})'); continue
            log.append(f'END {v} {kj} {sg}' + (' UNRULED' if 'UNRULED' in o else '')); break
        nsub = 0
        (tp, res), d, n, fresh = ff
        # representatives: stable symbols (old) get t = tgen, fresh gets much larger
        toks = parse(tp); vals = []
        old = sorted(set(re.findall(r'X\d+', tp)) - fresh, key=lambda x: int(x[1:]))
        rep = {}
        for x in old:
            if x not in res: log.append('NORES ' + x); return log
            rep[x] = res[x] % RM + RM * tgen
        newt = []
        for (w, e), dd in zip(toks, d):
            co, c = lin(e)
            val = c + dd * n + sum(v * rep[x] for x, v in co.items() if x in rep)
            newt.append([w, co, val])
        mx = max([abs(v[2]) for v in newt] + [1])
        tf = tgen
        for x in fresh:
            if x not in res: log.append('NORES ' + x); return log
        while res[next(iter(fresh))] % RM + RM * tf <= 2 * mx if fresh else False: tf *= 2
        for x in fresh: rep[x] = res[x] % RM + RM * tf
        tgen = tf * 2
        parts = []
        for w, co, val in newt:
            val += sum(v * rep[x] for x, v in co.items() if x in fresh)
            if val < 0: log.append('NEGEXP'); return log
            parts.append(f'{w}^{val}' if (co or val != 1 or True) else w)
        key = re.sub(r'\d+', '#', ' '.join(f'{w}' for w, _, _ in newt))
        nff += 1
        log.append(f'FF{nff} n={n} d={",".join(str(x) for x in d if x)}')
        tape = ' '.join(p if not p.endswith('^1') else p[:-2] for p in parts if not p.endswith('^0'))
        if tape.endswith('>'): pass
    else:
        log.append('ROUNDS-DONE')
    return log
if __name__ == '__main__':
    lst, out = sys.argv[1:3]; rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 6; bud = int(sys.argv[4]) if len(sys.argv) > 4 else 6000
    done = set(l.split()[0] for l in open(out)) if os.path.exists(out) else set()
    fo = open(out, 'a')
    for line in open(lst):
        p = line.rstrip('\n').split('\t')
        if len(p) < 2 or p[0] in done: continue
        log = grade(p[0], p[1], rounds, bud, p[2] if len(p) > 2 else '')
        fo.write(p[0] + ' | ' + ' || '.join(log) + '\n'); fo.flush()
