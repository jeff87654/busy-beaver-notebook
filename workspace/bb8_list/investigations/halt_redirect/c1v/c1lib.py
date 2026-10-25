"""c1lib.py: driver for c1sim.exe (own verifier tools for the c1 machine).  Fails loudly on anything unexpected."""
import subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, os.environ.get('C1EXE', 'c1sim.exe'))
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
C1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---1LJ_0RJ0RF'
BASE = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_0RG1LD_1RH1LG_1LC0RG'
_sv = None
def sv():
    global _sv
    if _sv is None or _sv.poll() is not None:
        _sv = subprocess.Popen([EXE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1, creationflags=LOW)
    return _sv
def expand(toks):
    """toks: list of ints or (value, count) pairs or 'v^k' strings -> flat list"""
    out = []
    for t in toks:
        if isinstance(t, tuple): out += [t[0]] * t[1]
        elif isinstance(t, str) and '^' in t: v, k = t.split('^'); out += [int(v)] * int(k)
        else: out.append(int(t))
    return out
def word(toks):
    return ''.join('10' * m + '1' for m in toks) + '1010'
def spec(toks):
    """compressed comma spec"""
    out = []; i = 0
    while i < len(toks):
        j = i
        while j < len(toks) and toks[j] == toks[i]: j += 1
        out.append(f'{toks[i]}^{j-i}' if j - i > 1 else str(toks[i])); i = j
    return ','.join(out)
def job(mode, machine, maxs, bits, head, state, target=None):
    s = sv()
    s.stdin.write(f'{mode} {machine} {maxs} {bits}:{head}:{state} {spec(target) if target else "-"}\n'); s.stdin.flush()
    if mode == 'reach':
        line = s.stdout.readline().strip()
        if not line: raise RuntimeError('no output from c1sim')
        return line
    lines = []
    while True:
        line = s.stdout.readline()
        if not line: raise RuntimeError('c1sim died')
        line = line.strip(); lines.append(line)
        if not line.startswith('K '): return lines
def reach(toks, target, machine=C1, maxs=10**9, far=''):
    """start = K-moment of toks (farthest-first incl a, r), optional far prefix bits; returns parsed result"""
    toks = expand(toks); target = expand(target)
    w = far + word(toks)
    line = job('reach', machine, maxs, w, len(w), 'G', target)
    f = line.split()
    return f
def kstart(b):
    """record-family K(0^35; 0; b) word for the GH family, head on the blank right of it, state G"""
    return '1' + '011' * 36 + '01' * (3 * b + 1) + '1010'
def tok_rle(v):
    return spec(v).replace(',', ' ')
def stage(bits, head, state, machine=C1, maxs=2 * 10**9, cap=3000):
    s = sv()
    s.stdin.write(f'stage {machine} {maxs} {bits}:{head}:{state} - {cap}\n'); s.stdin.flush()
    line = s.stdout.readline().strip()
    if not line: raise RuntimeError('no output from c1sim')
    return line
