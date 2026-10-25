"""lib.py -- helpers around sim.exe (bb10_c35exc_verify). Every process runs at IDLE priority."""
import subprocess, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.join(HERE, 'sim.exe')
IDLE = 0x40

M10 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0LD0RH_1RG1LF_0LJ1RI_---0LA'
R8 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF'


_proc = None


def _get_proc():
    global _proc
    if _proc is None or _proc.poll() is not None:
        _proc = subprocess.Popen([SIM, 'batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 text=True, creationflags=IDLE, bufsize=1)
    return _proc


last_hist = []


def run(machine, left, state, right, maxsteps, opts=(), timeout=None):
    """returns (snaps, end); snaps = [(step, L, S, R)], end = (reason, step, L, S, R).
    Uses one persistent IDLE-priority sim.exe in batch mode."""
    global last_hist
    p = _get_proc()
    line = ' '.join([machine, left or '-', state, right or '-', str(maxsteps)] + list(opts))
    p.stdin.write(line + '\n'); p.stdin.flush()
    snaps, end, hist = [], None, []
    while True:
        l = p.stdout.readline()
        if not l:
            raise RuntimeError('sim died')
        l = l.rstrip('\n')
        if l == 'DONE':
            break
        if l.startswith('SNAP '):
            parts = l.split(' ')
            step, cfg = parts[1], parts[2]
            mh = int(parts[3]) if len(parts) > 3 else 0
            L, S, R = cfg.split('|')
            snaps.append((int(step), '' if L == '-' else L, S, R, mh))
        elif l.startswith('HIST '):
            hist.append(l)
        elif l.startswith('END '):
            parts = l.split(' ')
            reason, step = parts[1], int(parts[2])
            if len(parts) > 3:
                L, S, R = parts[3].split('|')
                end = (reason, step, '' if L == '-' else L, S, R)
            else:
                end = (reason, step, None, None, None)
    last_hist = hist
    if end is None:
        raise RuntimeError('sim failed for ' + line[:200])
    return snaps, end


def rle(s):
    """compact run-length view of a 0/1 string: groups (10)^k and 1^k etc. for eyeballing"""
    out = []
    i = 0
    while i < len(s):
        # (10)^k with k >= 2
        k = 0
        while s.startswith('10', i + 2 * k):
            k += 1
        if k >= 2:
            out.append('(10)^%d' % k); i += 2 * k; continue
        k = 0
        while s.startswith('01', i + 2 * k):
            k += 1
        if k >= 2:
            out.append('(01)^%d' % k); i += 2 * k; continue
        c = s[i]; j = i
        while j < len(s) and s[j] == c:
            j += 1
        out.append(c if j - i == 1 else '%s^%d' % (c, j - i))
        i = j
    return ' '.join(out)


def tokens(s):
    """parse a 0/1 string (leading zeros stripped) into D-tokens: D(n) = 1 (01)^n.
    returns a list of ints (n) and strings for unparsed stretches (e.g. '00', '0', '11')."""
    s = s.lstrip('0')
    out = []
    i = 0
    while i < len(s):
        if s[i] == '1':
            n = 0
            i += 1
            while s.startswith('01', i):
                n += 1; i += 2
            out.append(n)
        else:
            j = i
            while j < len(s) and s[j] == '0':
                j += 1
            out.append('0' * (j - i) if j - i <= 3 else '0^%d' % (j - i))
            i = j
    return out


def ctok(toks):
    """compress a token list: runs of equal tokens -> 'n^k'"""
    out = []
    i = 0
    while i < len(toks):
        j = i
        while j < len(toks) and toks[j] == toks[i]:
            j += 1
        t = toks[i]
        out.append(('D%s' % t if isinstance(t, int) else t) + ('^%d' % (j - i) if j - i > 1 else ''))
        i = j
    return ' '.join(out)


def D(n):
    return '1' + '01' * n


def word(toks):
    return ''.join(D(t) for t in toks)


def macro_steps(machine, toks, maxsteps, maxsnap=None):
    """run from word(toks) G> 0^inf; return list of (step, tokens) at each right-edge G0 event"""
    opts = ['snap=G0']
    if maxsnap:
        opts.append('maxsnap=%d' % maxsnap)
    snaps, end = run(machine, word(toks), 'G', '0', maxsteps, opts)
    out = []
    for s in snaps:
        if s[3].strip('0') != '':
            raise RuntimeError('snapshot with nonblank right part')
        t = tokens(s[1])
        out.append((s[0], t))
    return out, end


def diff(t1, t2):
    """common prefix length, then the changed suffixes"""
    k = 0
    while k < len(t1) and k < len(t2) and t1[k] == t2[k]:
        k += 1
    return k, t1[k:], t2[k:]


def next_bform(machine, toks, maxsteps, skip_first=True):
    """run from word(toks) G> and return (step, tokens) of the first later right-edge G0 event whose
    token list ends with [0, y] (B-form); or (None, end) if none within maxsteps"""
    opts = ['snap=G0']
    snaps, end = run(machine, word(toks), 'G', '0', maxsteps, opts + ['maxsnap=100000'])
    for s in snaps:
        if s[0] == 0 and skip_first:
            continue
        if s[3].strip('0') != '':
            raise RuntimeError('nonblank right part')
        t = tokens(s[1])
        if len(t) >= 2 and t[-2] == 0 and all(isinstance(q, int) for q in t):
            return s[0], t
    return None, end


def bforms(machine, toks, maxsteps, maxsnap=200000):
    """all B-form right-edge G0 events (step, tokens) from word(toks) G>, plus the end record"""
    snaps, end = run(machine, word(toks), 'G', '0', maxsteps, ['snap=G0', 'bform', 'maxsnap=%d' % maxsnap])
    out = []
    for s in snaps:
        if s[3].strip('0') != '':
            raise RuntimeError('nonblank right part')
        t = tokens(s[1])
        if len(t) >= 2 and t[-2] == 0 and all(isinstance(q, int) for q in t):
            out.append((s[0], t))
    return out, end


def is_R12(t1, t2):
    """does t1 -> t2 follow R1 or R2 (token-count form)?"""
    if t1[-2] != 0:
        return None
    y = t1[-1]
    i = len(t1) - 3
    k = 0
    while i >= 0 and t1[i] == 1:
        k += 1; i -= 1
    if i < 0:
        return None
    x = t1[i]
    if x < 4:
        return None
    if k == 0:
        exp = t1[:i] + [x - 3, 0, 2 * y + 8]
        name = 'R1'
    else:
        exp = t1[:i] + [x - 3, y + 3] + [1] * (k - 1) + [0, 4]
        name = 'R2'
    return name if exp == t2 else None
