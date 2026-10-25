"""Literal stage tester for the GH 0LH machine: run one literal stage (stage35g server via mf35g.run_stage) from a
token configuration [farthest-first tokens ..., a, r] (+ optional far bits), print the K-moment / halt.
usage: python st.py "9^13 6 24 10 0 0 32 4 0 0 1 3" A R [--far BITS] [--maxs N]
Tokens accept RLE  x^k."""
import sys, argparse
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import mf35g, mf35
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH_------'
FAM = 'GH'
F = mf35g.FAMILIES[FAM]

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

def run(tokens, a, r, far='', maxs=200_000_000):
    """tokens: list of ints farthest-first (without a, r).  Returns dict kind=K/H/T/W, toks (farthest-first), a, r, far, step"""
    word = far + mf35.word_of_tokens(list(tokens) + [a, r]) + F['SUF']
    out = mf35g.run_stage(FAM, M, word, len(word), F['Q'], maxs)
    f = out.split()
    if f[0] == 'H':
        return {'kind': 'H', 'state': f[2], 'read': f[3], 'ones': int(f[4]), 'step': int(f[1]), 'raw': out}
    if f[0] in ('T', 'W'):
        return {'kind': f[0], 'step': int(f[1]), 'raw': out}
    parts = out.split('|')
    toks = [int(x) for x in parts[1].split()]
    farb = parts[2].strip() if len(parts) > 2 else ''
    return {'kind': 'K', 'toks': toks[2:][::-1], 'a': toks[1], 'r': toks[0], 'far': farb, 'step': int(f[1]), 'raw': out}

def fmt(o):
    if o['kind'] == 'K':
        return f"K: {rle(o['toks'])} | a={o['a']} r={o['r']}" + (f" far={o['far'][:60]}..(len {len(o['far'])})" if o['far'] else '') + f" step={o['step']}"
    if o['kind'] == 'H':
        return f"HALT {o['state']}{o['read']} ones={o['ones']} step={o['step']}"
    return o['raw'][:80]

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('tokens'); ap.add_argument('a', type=int); ap.add_argument('r', type=int)
    ap.add_argument('--far', default=''); ap.add_argument('--maxs', type=int, default=200_000_000)
    x = ap.parse_args()
    print(fmt(run(expand(x.tokens), x.a, x.r, x.far, x.maxs)))
