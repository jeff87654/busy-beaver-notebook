"""rlib.py: driver for rtwin.exe (env RTWIN overrides; right-end survival twin runs).  twin(M, word, gap, pat) -> dict"""
import subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sim import far_of, word_of, expand, N1
L12 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LC1LL_0LK0RC'
_sv = None
def server():
    global _sv
    if _sv is None or _sv.poll() is not None:
        _sv = subprocess.Popen([os.path.join(HERE, '' + os.environ.get('RTWIN', 'rtwin.exe') + '')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                               bufsize=1, creationflags=0x40)
    return _sv
def rle(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]: j += 1
        out.append(f'{v[i]}^{j-i}' if j - i > 1 else str(v[i])); i = j
    return ' '.join(out)
def parse_out(s):
    s = s.strip()
    if not s.startswith('K'):
        return {'kind': s.split()[0], 'raw': s}
    f = s.split('|')
    toks = [int(x) for x in f[1].split()]
    far = f[2].strip()
    rem, off = f[3].strip()[4:].split(' @')
    return {'kind': 'K', 'steps': int(f[0].split()[1]), 'toks': toks, 'far': far, 'rem': rem, 'off': int(off),
            'desc': rle(toks[2:][::-1]) + f' | a={toks[1]} r={toks[0]}'}
def twin(M, word, gap=4, pat='-', maxs=10**8, rcap=600):
    sv = server()
    sv.stdin.write(f'{M} G {len(word)} {maxs} {rcap} {gap} {pat or "-"}\n{word}\n'); sv.stdin.flush()
    line = sv.stdout.readline()
    b, rd, dv, p = line.split(' | R ')[0], *line.split(' | R ')[1].split(' | V ')[0:1], None, None
    parts = line.strip().split(' | ')
    # parts: 'B ...K steps' , toks, far, 'rem=.. @.. bmax=..', 'R ..', 'V ..', 'P ...', ...
    i_r = [i for i, x in enumerate(parts) if x.startswith('R ')][0]
    bpart = ' | '.join(parts[:i_r]); bmax = int(bpart.rsplit('bmax=', 1)[1]); bpart = bpart.rsplit(' bmax=', 1)[0][2:]
    ppart = ' | '.join(parts[i_r + 2:])[2:]
    return {'base': parse_out(bpart), 'bmax': bmax, 'read': parts[i_r][2:], 'div': parts[i_r + 1][2:], 'pat': parse_out(ppart),
            'raw': line.strip()}
def word(toks, far=''):
    if isinstance(toks, str): toks = expand(toks)
    return far + word_of(toks) + '1010'
