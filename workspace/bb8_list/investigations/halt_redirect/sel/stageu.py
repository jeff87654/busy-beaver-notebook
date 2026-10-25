"""stageu.py: run one literal stage (stage35g server, family GH) from a token configuration and report the K/H result
AND the slots read.  usage: python stageu.py MACHINE "tokens incl a r" [--far BITS] [--maxs N] [--xstart B0]
As a module: stage(machine, tokens, far='', maxs=...) -> (outline, slots)"""
import sys, subprocess, argparse, os
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import mf35g, mf35
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
SL = ['A0','A1','B0','B1','C0','C1','D0','D1','E0','E1','F0','F1','G0','G1','H0','H1','I0','I1','J0','J1']
_sv = None
def server():
    global _sv
    if _sv is None or _sv.poll() is not None:
        _sv = subprocess.Popen([mf35g.STAGE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1, creationflags=LOW)
    return _sv
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
def run_word(machine, word, head, state, maxs=50_000_000, fam='GH', rcap=600):
    F = mf35g.FAMILIES[fam]
    if machine.count('_') == 8: machine += '_------'
    sv = server(); q = 'ABCDEFGHIJ'.index(F['Q'])
    sv.stdin.write(f"{machine} {state} {head} {maxs} {4*len(word)+20000} {rcap} {q} {F['SUF']} {F['E']}\n{word}\n"); sv.stdin.flush()
    line = sv.stdout.readline().strip()
    out, _, u = line.rpartition(' | U=')
    um = int(u, 16) if _ else 0
    return out, [SL[i] for i in range(20) if um >> i & 1]
def stage(machine, tokens, far='', maxs=50_000_000, fam='GH'):
    F = mf35g.FAMILIES[fam]
    if isinstance(tokens, str): tokens = expand(tokens)
    word = far + mf35.word_of_tokens(tokens) + F['SUF']
    return run_word(machine, word, len(word), F['Q'], maxs, fam)
def fmt(out):
    f = out.split()
    if f[0] == 'H': return f'HALT {f[2]}{f[3]} ones={f[4]} step={f[1]}'
    if f[0] in ('T', 'W'): return out[:60]
    parts = out.split('|'); toks = [int(x) for x in parts[1].split()]; far = parts[2].strip() if len(parts) > 2 else ''
    return f'K: {rle(toks[2:][::-1])} | a={toks[1]} r={toks[0]}' + (f' far={far[:40]}(len {len(far)})' if far else '') + f' step={f[1]}'
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('tokens', nargs='?', default=None)
    ap.add_argument('--far', default=''); ap.add_argument('--maxs', type=int, default=50_000_000); ap.add_argument('--xstart', type=int, default=None)
    ap.add_argument('--fam', default='GH')
    a = ap.parse_args()
    if a.xstart is not None:
        w, h, s = mf35g.xstart(a.fam, a.xstart); out, sl = run_word(a.machine, w, h, s, a.maxs, a.fam)
    else:
        out, sl = stage(a.machine, a.tokens, a.far, a.maxs, a.fam)
    print(fmt(out)); print('slots:', ' '.join(sl))
