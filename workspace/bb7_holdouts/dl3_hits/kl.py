"""kl.py: K-level literal probes via kview.exe (idle priority).
   T = tmpl(machine) from out.tsv;  word(T, ds, a, b);  run(M, ds, a, b, steps, nchg, maxl) -> list of events
   event = ('K', step, ds_list, a, b) | ('H', step, state, read) | ('?', step, rl) | ('END',)"""
import idle, subprocess, re
from pathlib import Path
H = Path(__file__).resolve().parent
EXE = str(H / 'kview.exe')
_rows = {l.split('\t')[0]: l.split('\t') for l in (H / 'out.tsv').read_text().splitlines()[1:] if '\t' in l}
def tmpl(m, t=None):
    t = t or _rows[m][4]
    o, q, rest = t.split(',', 2)
    d = dict(x.split('=', 1) for x in rest.split(','))
    al, be = map(int, re.fullmatch(r'(\d+)d\+(-?\d+)', d['d']).groups()); alB, beB = map(int, re.fullmatch(r'(\d+)b\+(-?\d+)', d['b']).groups())
    P = '' if d['P'] == '-' else d['P']; S = '' if d['S'] == '-' else d['S']
    return dict(o=o, q=q, P=P, u=d['u'], s=d['s'], al=al, be=be, alB=alB, beB=beB, S=S)
def word(T, ds, a, b):
    return T['P'] + ''.join(T['u'] * (T['al'] * x + T['be']) + T['s'] for x in list(ds) + [a]) + T['u'] * (T['alB'] * b + T['beB']) + T['S']
def expand(dstr):
    out = []
    for x in dstr.strip(',').split(','):
        if not x: continue
        if '^' in x: v, n = x.split('^'); out += [int(v)] * int(n)
        else: out.append(int(x))
    return out
def args(T):
    return [T['o'], T['q'], T['P'] or '-', T['u'], T['s'], str(T['al']), str(T['be']), str(T['alB']), str(T['beB']), T['S'] or '-']
def parse(out):
    ev = []
    for l in out.splitlines():
        m = re.match(r'(\d+) K\((.*); (-?\d+); (-?\d+)\) len', l)
        if m: ev.append(('K', int(m[1]), expand(m[2]), int(m[3]), int(m[4]))); continue
        m = re.match(r'HALT (\d+) state (\w) read (\d)', l)
        if m: ev.append(('H', int(m[1]), m[2], int(m[3]))); continue
        m = re.match(r'(\d+) \? (.*)', l)
        if m: ev.append(('?', int(m[1]), m[2])); continue
        if l.startswith('END'): ev.append(('END',))
    return ev
def run(M, ds, a, b, steps=10**8, nchg=2, maxl=200, T=None, pall=0, w=None):
    T = T or tmpl(M)
    w = w if w is not None else word(T, ds, a, b)
    cmd = [EXE, M] + args(T) + [str(steps), str(maxl), str(pall), w, str(len(w)), T['q'], str(nchg)]
    p = subprocess.Popen(cmd, creationflags=0x40, stdout=subprocess.PIPE, text=True)
    o, _ = p.communicate()
    return parse(o)
def blank(M, steps, maxl=200, T=None):
    T = T or tmpl(M)
    p = subprocess.Popen([EXE, M] + args(T) + [str(steps), str(maxl)], creationflags=0x40, stdout=subprocess.PIPE, text=True)
    o, _ = p.communicate(); return parse(o)
