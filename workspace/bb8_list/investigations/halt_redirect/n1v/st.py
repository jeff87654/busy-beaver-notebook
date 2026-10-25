"""n1v/st.py: literal stage driver for n1 (family GH) via stage35g server.
tokens farthest-first incl. a and r; word = far + tokens + SUF; head at end, state G.
stage(far, toks) -> dict(kind, step, toks(farthest-first incl a,r), far) or HALT info"""
import sys, os
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import mf35g, mf35
from follow2 import Aff, Fail, jump
N1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
F = mf35g.FAMILIES['GH']

def expand(s):
    v = []
    for t in s.split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        else:
            v.append(int(t))
    return v

def rle(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]:
            j += 1
        out.append(f'{v[i]}^{j-i}' if j - i > 1 else str(v[i])); i = j
    return ' '.join(out)

def stage(far, toks, maxs=200_000_000, machine=N1, rcap=600):
    word = far + mf35.word_of_tokens(toks) + F['SUF']
    out = mf35g.run_stage('GH', machine, word, len(word), F['Q'], int(maxs), rcap=rcap)
    f = out.split()
    if not f:
        return {'kind': 'NOOUT', 'raw': out}
    if f[0] == 'H':
        return {'kind': 'HALT', 'step': int(f[1]), 'state': f[2], 'read': f[3], 'ones': int(f[4]), 'raw': out}
    if f[0] in ('T', 'W'):
        return {'kind': f[0], 'raw': out[:200]}
    parts = out.split('|')
    tk = [int(x) for x in parts[1].split()]
    far2 = parts[2].strip() if len(parts) > 2 else ''
    return {'kind': 'K', 'step': int(f[1]), 'toks': tk[::-1], 'far': far2, 'raw': out[:80]}

def fmt(res):
    if res['kind'] != 'K':
        return res['kind'] + ' ' + res.get('raw', '')
    t = res['toks']
    return f"{rle(t[:-2])} | a={t[-2]} r={t[-1]}" + (f" far[{len(res['far'])}]={res['far']}" if res['far'] else '')

def dojump(toks, E=1):
    """abstract jump; returns (items as concrete token list with params unresolved -> list of (Aff m, Aff c)), newp, info"""
    digits = toks[:-2]
    ent = []
    for m in digits:
        if ent and ent[-1][1] == m:
            ent[-1][2] += 1
        else:
            ent.append(['D', m, 1])
    left = [('D', Aff(m), Aff(c)) for _, m, c in ent] + [('D', Aff(toks[-2]), Aff(1)), ('D', Aff(toks[-1]), Aff(1))]
    return jump(left, [], {}, E)

if __name__ == '__main__':
    far = sys.argv[1] if sys.argv[1] != '-' else ''
    toks = expand(sys.argv[2])
    r = stage(far, toks)
    print(fmt(r), '| step', r.get('step'))
