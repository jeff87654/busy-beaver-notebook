"""Size-ordered re-check of follow2 stage results (the M3 lesson: in the real run a newer accumulator is far larger
than every older one, while follow2 samples all parameters at comparable sizes).
For every stage of a machine's logs/<m>.stages.pkl whose input has two or more symbolic parameters and whose result
is a jump, the input is instantiated with the OLDER parameters small (b = 6, R_i = 20) and the NEWEST parameter large
(R = NEWR, default 2000, at least 10x every list length), simulated with hyb10r, and compared literally with the
follower's fitted output at the same values.
  python ordercheck.py MACHINES.txt OUT.tsv [NEWR]
OUT: machine, stage, verdict (SAME / DIFFERENT / RUN-FAIL / SKIP), values, observed head (first 160 chars)."""
import math, os, pickle, re, sys, __main__
from fractions import Fraction
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault('HYBEXE', 'hyb10r.exe')
import follow2 as f, numres
for k in dir(f):
    if not k.startswith('_'):
        setattr(__main__, k, getattr(f, k))
setattr(__main__, 'Num', numres.Num)

def p_expr(s):
    s = s.strip()
    a = f.Aff(0)
    for sign, term in re.findall(r'([+-]?)([^+-]+)', s):
        k = -1 if sign == '-' else 1
        if '*' in term:
            c, n = term.split('*'); a = a + f.Aff(0, {n: Fraction(c) * k})
        elif re.fullmatch(r'[0-9/]+', term):
            a = a + f.Aff(Fraction(term) * k)
        else:
            a = a + f.Aff(0, {term: k})
    return a

def parse_fmt(s):
    pos = 0
    def count():
        nonlocal pos
        if s.startswith('^{', pos):
            j = s.index('}', pos); c = p_expr(s[pos + 2:j]); pos = j + 1; return c
        return f.Aff(1)
    def seq(stop):
        nonlocal pos
        out = []
        while pos < len(s):
            if s[pos] == ' ':
                pos += 1; continue
            if stop and s[pos] == stop:
                return out
            if s.startswith('D(', pos):
                j = s.index(')', pos); p = p_expr(s[pos + 2:j]); pos = j + 1
                out.append(('D', p, count()))
            elif s[pos] == '<':
                j = s.index('>', pos); runs = []
                for part in s[pos + 1:j].split('.'):
                    pat, k = part.rsplit('^', 1); pat = pat.strip('()'); runs.append((pat, p_expr(k)))
                pos = j + 1; out.append(('J', tuple(runs), count()))
            elif re.match(r'\((10|01)\)\^', s[pos:]):
                m = re.match(r'\((10|01)\)\^([^ ]+)', s[pos:]); pos += m.end()
                out.append(('R', (m.group(1), p_expr(m.group(2))), f.Aff(1)))
            elif s[pos] == '(':
                pos += 1; inner = seq(')'); pos += 1
                out.append(('B', tuple(inner), count()))
            elif s[pos] in '01':
                m = re.match(r'([01])\^([0-9]+)', s[pos:]); pos += m.end()
                out.append(('R', (m.group(1), f.Aff(int(m.group(2)))), f.Aff(1)))
            else:
                raise ValueError(f'cannot parse at {pos}: {s[pos:pos+30]!r}')
        return out
    return seq(None)

def lens(sym, vals):
    try:
        return max([f.A(c).at(vals) for k, p, c in sym if k == 'D'] + [0])
    except Exception:
        return 0

def check(m, newr):
    pk = HERE / 'logs' / f'{m}.stages.pkl'
    log = HERE / 'logs' / f'{m}.log'
    if not pk.exists():
        return [(m, '-', 'SKIP', 'no stages.pkl', '')]
    st = pickle.load(open(pk, 'rb'))
    txt = log.read_text(errors='ignore') if log.exists() else ''
    q = 'A' if re.search(r'^stage 0: input\s*$', txt, re.M) else ('G' if 'template R,G' in txt else 'B')
    mq = re.search(r'K-moments found in state (\w)', txt)
    if mq:
        q = mq.group(1)
    rows = []
    for i, (fin, res) in enumerate(st):
        if res.get('kind') != 'J' or not fin.strip():
            continue
        sym = parse_fmt(fin)
        ps = sorted(f.params_in(sym), key=lambda p: (p != 'b', int(p[1:]) if p[1:].isdigit() else 0))
        if len(ps) < 2:
            continue
        mod = {}
        for p in ps:
            mm = (3 if p.startswith('R') else 1) * res.get('period', {}).get(p, 1)
            for x in f.all_affs(sym):
                if p in x.co:
                    d = x.co[p].denominator
                    mm = mm * d // math.gcd(mm, d)
            mod[p] = mm
        base = res.get('vals', {})
        def near(p, target):
            b0 = base.get(p, target)
            return target + ((b0 - target) % mod[p])
        vals = {p: near(p, 6 if p == 'b' else 12) for p in ps}
        newest = ps[-1]
        if newest == 'b':
            continue
        vals[newest] = near(newest, max(newr, 10 * lens(sym, vals)))
        try:
            w = f.word_of(f.inst(sym, vals))
            o = f.run_hyb(m, w, 3_000_000_000, start=q, canon=q)
        except Exception as e:
            rows.append((m, str(i), 'RUN-FAIL', str(vals), str(e)[:160])); continue
        if o['kind'] != 'J':
            rows.append((m, str(i), 'DIFFERENT', str(vals), o['raw'][:160])); continue
        try:
            pred = f.word_of(f.inst(res['left'] + res['tail'], vals))
            obs = f.word_of(o['left'] + o['tail'])
            same = pred == obs
        except Exception as e:
            rows.append((m, str(i), 'RUN-FAIL', str(vals), 'compare: ' + str(e)[:140])); continue
        rows.append((m, str(i), 'SAME' if same else 'DIFFERENT', str(vals), o['raw'][:160]))
    return rows

if __name__ == '__main__':
    ms = [l.split()[0] for l in open(sys.argv[1]) if l.strip()]
    newr = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    out = Path(sys.argv[2])
    done = {l.split('\t')[0] for l in out.read_text().splitlines()} if out.exists() else set()
    with out.open('a') as fo:
        for m in ms:
            if m in done:
                continue
            for r in check(m, newr):
                fo.write('\t'.join(r) + '\n'); fo.flush()
                print(*r[:4], flush=True)
