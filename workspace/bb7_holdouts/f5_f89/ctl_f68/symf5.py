"""symf5.py: SOUND symbolic check of the F5 macro rules with symsim (never_audit/src/symsim.exe).
Config (A, L, c) with entries int or symbolic ('H', residue) ; tape built in the mirrored orientation (K at right):
  rev(content) 0^2 Q>   content = (10)^A 0 [(10)^d 0]* (10)^e 1 [(10)^c 1]
Runs symsim to successive Q-stops, parses each stop back into (A,L,c) with Lin entries, returns first template config."""
import sys, os, re, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\never_audit')
from sym import Lin, parse_expr, mirror
DEBUG = False
SYMSIM = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\never_audit\src\symsim.exe'
def T(t, s): return isinstance(t, str) and t == s
def cnt(x):
    if isinstance(x, tuple): return 'H%d' % x[1]
    return str(x)
def build(A, L, c):
    # reversed content as symsim tokens (left to right)
    toks = []
    if c != -1: toks += ['1'] + (['01^' + cnt(c)] if c != 0 else [])
    toks += ['1']
    e = L[-1]
    if e != 0: toks.append('01^' + cnt(e))
    for d in reversed(L[:-1]):
        toks.append('0')
        if d != 0: toks.append('01^' + cnt(d))
    toks.append('0')
    if A != 0: toks.append('01^' + cnt(A))
    toks.append('0^2')
    return ' '.join(toks)
def parse_items(tp):
    items = []; q = None
    for t in tp.split():
        if len(t) == 2 and t[1] == '>': q = t[0]; break
        if t == '...': return None
        if '^' in t:
            w, cs = t.split('^', 1); items.append((w, parse_expr(cs)))
        else: items.append((t, Lin.c(1)))
    return items
def to_config(items):
    """items: tape runs left->right up to the head (mirrored orientation). -> (A, L, c) with Lin entries, or None"""
    pcs = []
    for w, n in items:
        if n.isconst() and n.const() <= 400: s = w * int(n.const())
        else: pcs.append(('B', w, n)); continue
        if pcs and isinstance(pcs[-1], str): pcs[-1] += s
        else: pcs.append(s)
    if not pcs or not isinstance(pcs[-1], str): return None
    last = pcs[-1].rstrip('0'); z = len(pcs[-1]) - len(last)
    if z != 2: return None
    pcs[-1] = last
    if pcs[-1] == '': pcs.pop()
    # reverse into content order
    rp = []
    for p in reversed(pcs):
        if isinstance(p, str): rp.append(p[::-1])
        else: rp.append(('B', p[1][::-1], p[2]))
    # canonicalize blocks
    cp = []
    for p in rp:
        if isinstance(p, str): cp.append(p); continue
        w, n = p[1], p[2]
        if w == '10': cp.append(('U', n))
        elif w == '01': cp += ['0', ('U', n - 1), '1']
        elif len(w) == 5 and any(w[i:] + w[:i] == '10100' for i in range(5)):
            i = [i for i in range(5) if w[i:] + w[:i] == '10100'][0]
            cp += [w[:i], ('R2', n - 1), w[i:]]
        else: return ('UNPARSED', w, n)
    while cp and isinstance(cp[-1], str) and set(cp[-1]) <= {'0'}: cp.pop()
    if cp and isinstance(cp[-1], tuple) and cp[-1][0] == 'U': cp[-1:] = [('U', cp[-1][1] - 1), '1']
    toks = []
    def addu(n):
        if toks and isinstance(toks[-1], Lin): toks[-1] = toks[-1] + n
        else: toks.append(n)
    # flatten: merge strings, tokenize
    buf = ''
    def flush(nextc):
        nonlocal buf
        s = buf; i = 0
        while i < len(s):
            if s.startswith('10', i): addu(Lin.c(1)); i += 2
            elif s[i] == '0': toks.append('.'); i += 1
            elif i == len(s) - 1 and nextc == 'U': toks.append('#'); i += 1   # '1' followed by (10)^n block -> lone 1
            else: toks.append('#'); i += 1
        buf = ''
    for p in cp:
        if isinstance(p, str): buf += p
        elif p[0] == 'R2':
            flush('R'); toks.append(('R2', p[1]))
        else:
            flush('U'); addu(p[1])
    flush(None)
    while toks and T(toks[0], '.'): toks.pop(0)
    while toks and T(toks[-1], '.'): toks.pop()
    i = 0
    if not toks or not isinstance(toks[0], Lin): return None
    A = toks[0]; i = 1
    if i >= len(toks) or not T(toks[i], '.'): return None
    i += 1; L = []
    while True:
        if i < len(toks) and isinstance(toks[i], tuple):   # ('R2', n): n copies of digit 2 (each '2 .')
            L.append(toks[i]); i += 1; continue
        v = Lin.c(0)
        if i < len(toks) and isinstance(toks[i], Lin): v = toks[i]; i += 1
        if i >= len(toks): return None
        sep = toks[i]; i += 1; L.append(v)
        if T(sep, '#'): break
        if not T(sep, '.'): return None
    c = Lin.c(-1)
    if i < len(toks):
        if not isinstance(toks[i], Lin) or i + 2 != len(toks) or not T(toks[i + 1], '#'): return None
        c = toks[i]
    return (A, L, c)
def run(M, q, A, L, c, mg=2, hlb=100, maxstops=60, budget=400000, tl=60):
    tape = build(A, L, c) + ' ' + q + '>'
    args = [SYMSIM, 'run', '--noch', '--nokt', '--mg', str(mg), '--budget', str(budget), '--stopq', q, '--stopn', str(maxstops),
            '--stopall', '--hlb', str(hlb), '--tlimit', str(tl)]
    p = subprocess.run(args, input='%s %s %s\n' % (M, q, tape), capture_output=True, text=True, timeout=tl * 3 + 30)
    verdict = None
    for l in p.stdout.splitlines():
        if l.startswith('STOP '):
            tp = l.split(' TAPE ', 1)[1].split(' |')[0]
            it = parse_items(tp)
            if it is None: continue
            cf = to_config(it)
            if DEBUG: print('  stop', tp[:150], '->', cf)
            if cf is not None and not (isinstance(cf, tuple) and isinstance(cf[0], str)): return 'K', cf, l
            if cf is not None: return 'PARSE', cf, l
        elif l.startswith('R '): verdict = l.split()[3:5]
    return 'NOK', verdict, p.stdout[-2000:]
if __name__ == '__main__':
    M3 = '1RB0LD_0RC0RG_1LD0RG_0LE---_1LB1LF_1LE1LG_0LA1RB'
    print(build(20, [0, 0, 30], -1))
    print(run(M3, 'G', 20, [0, 0, 30], -1))
    print(run(M3, 'G', ('H', 0), [0, 0, ('H', 0)], -1))
    print(run(M3, 'G', ('H', 0), [0, 0, 1], ('H', 1)))
