"""literal stage runner for the 1LD1LC machine (family GH): run(tokens farthest-first, a, r) -> dict
kind K: toks (farthest-first, without a and r), a, r, far, step;  kind H: state, read, ones, step;  T/W: step"""
import sys
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import mf35g, mf35
import os
MACHINES = {'GH': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LJ_1LD1LC',
            'REC': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_1LD1LC'}
FAM = os.environ.get('V_FAM', 'GH')          # V_FAM=REC selects the record-base machine (tail 10101)
M = MACHINES[FAM]
F = mf35g.FAMILIES[FAM]


def expand(s):
    v = []
    for t in str(s).split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        else:
            v.append(int(t))
    return v


def run(tokens, a, r, far='', maxs=2_000_000_000, machine=M):
    word = far + mf35.word_of_tokens(list(tokens) + [a, r]) + F['SUF']
    out = mf35g.run_stage(FAM, machine, word, len(word), F['Q'], maxs)
    f = out.split()
    if not f:
        raise RuntimeError('no output from stage server')
    if f[0] == 'H':
        return {'kind': 'H', 'state': f[2], 'read': int(f[3]), 'ones': int(f[4]), 'step': int(f[1]), 'raw': out}
    if f[0] in ('T', 'W'):
        return {'kind': f[0], 'step': int(f[1]), 'raw': out}
    if f[0] != 'J':
        raise RuntimeError('unexpected server line: ' + out[:200])
    parts = out.split('|')
    toks = [int(x) for x in parts[1].split()]
    farb = parts[2].strip() if len(parts) > 2 else ''
    return {'kind': 'K', 'toks': toks[2:][::-1], 'a': toks[1], 'r': toks[0], 'far': farb, 'step': int(f[1]), 'raw': out}


def rle(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]:
            j += 1
        out.append(f'{v[i]}^{j-i}' if j - i > 1 else str(v[i])); i = j
    return ' '.join(out)


def fmt(o):
    if o['kind'] == 'K':
        return (f"K: {rle(o['toks'])} | a={o['a']} r={o['r']}"
                + (f" far={o['far'][:40]}..(len {len(o['far'])})" if o['far'] else '') + f" step={o['step']}")
    if o['kind'] == 'H':
        return f"HALT {o['state']}{o['read']} ones={o['ones']} step={o['step']}"
    return o['raw'][:80]


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('tokens'); ap.add_argument('a', type=int); ap.add_argument('r', type=int)
    ap.add_argument('--far', default=''); ap.add_argument('--maxs', type=int, default=2_000_000_000)
    x = ap.parse_args()
    print(fmt(run(expand(x.tokens), x.a, x.r, x.far, x.maxs)))
