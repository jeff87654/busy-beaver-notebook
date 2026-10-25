"""Shared helpers for the f_{omega+1} verification (own code; no other agent's tools).

Tokens: D(m) = (10)^m 1.  tok(word) splits a 0/1 word into D tokens (a lone '0' run that is not part of a token is
kept as a literal 'z<k>' item).  run(jobs, ...) runs sim.exe at Idle priority."""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.join(HERE, 'sim.exe')
M10 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA'
REC8 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF'
IDLE = 0x40


def D(m):
    return '10' * m + '1'


def K(n, b, digits=None):
    """record template K(ds; 0; b): 1 (011)^(n+1) (01)^(3b+1) 10101, head right of it, state G (digits all 0)."""
    w = '1' + '011' * (n + 1) + '01' * (3 * b + 1) + '10101'
    return w, len(w), 'G'


TOKRE = re.compile(r'(?:10)*1|0+')


def tok(word):
    """list of items: int m for D(m), or 'z<k>' for a run of k zeros not absorbed by a token."""
    out = []
    i = 0
    n = len(word)
    while i < n:
        if word[i] == '0':
            j = i
            while j < n and word[j] == '0':
                j += 1
            # a single 0 followed by 1 could start a token only after a 1; here it is a free zero run
            out.append('z%d' % (j - i))
            i = j
            continue
        # word[i] == '1': take (10)^m 1 greedily but a '10' must be followed by '1' to continue
        j = i
        m = 0
        while j + 2 < n and word[j] == '1' and word[j + 1] == '0' and word[j + 2] == '1':
            j += 2
            m += 1
        # now word[j] == '1'
        out.append(m)
        i = j + 1
    return out


def rle(items):
    """run-length compress a token list -> list of (item, count)."""
    out = []
    for x in items:
        if out and out[-1][0] == x:
            out[-1][1] += 1
        else:
            out.append([x, 1])
    return out


def fmt(items):
    s = []
    for x, c in rle(items):
        t = ('D%d' % x) if isinstance(x, int) else x
        s.append(t if c == 1 else '%s^%d' % (t, c))
    return ' '.join(s)


def tokpos(word, head):
    """tokenize and locate the head: returns (items, idx, off) where items[idx] contains the head at offset off
    (idx == len(items) means right of the word)."""
    items = tok(word)
    pos = 0
    for k, x in enumerate(items):
        ln = (2 * x + 1) if isinstance(x, int) else int(x[1:])
        if head < pos + ln:
            return items, k, head - pos
        pos += ln
    return items, len(items), head - pos


def run(machine, jobs, maxsteps, events='-', maxrep=1, timeout=None):
    """jobs: list of (label, word, head, state). Returns list of parsed output lines (dicts)."""
    import tempfile
    fd, path = tempfile.mkstemp(suffix='.txt', dir=os.path.join(HERE, 'tmp'))
    with os.fdopen(fd, 'w') as f:
        for lab, w, h, q in jobs:
            f.write('%s %s %d %s\n' % (lab, w, h, q))
    try:
        p = subprocess.run([SIM, machine, path, str(maxsteps), events, str(maxrep)], capture_output=True, text=True,
                           creationflags=IDLE, timeout=timeout)
    finally:
        os.remove(path)
    res = []
    for line in p.stdout.splitlines():
        f = line.split()
        if f[0] == 'EV':
            res.append(dict(kind='EV', lab=f[1], n=int(f[2]), step=int(f[3]), q=f[4], c=int(f[5]), rel=int(f[6]),
                            word=f[7]))
        elif f[0] == 'HALT':
            res.append(dict(kind='HALT', lab=f[1], step=int(f[2]), q=f[3], c=int(f[4]), ones=int(f[5]), rel=int(f[6]),
                            word=f[7] if len(f) > 7 else ''))
        elif f[0] == 'STOP':
            res.append(dict(kind='STOP', lab=f[1], step=int(f[2])))
        elif f[0] == 'TIMEOUT':
            res.append(dict(kind='TIMEOUT', lab=f[1], step=int(f[2])))
    return res


os.makedirs(os.path.join(HERE, 'tmp'), exist_ok=True)


def parse(line):
    f = line.split()
    if f[0] == 'EV':
        return dict(kind='EV', lab=f[1], n=int(f[2]), step=int(f[3]), q=f[4], c=int(f[5]), rel=int(f[6]), word=f[7])
    if f[0] == 'HALT':
        return dict(kind='HALT', lab=f[1], step=int(f[2]), q=f[3], c=int(f[4]), ones=int(f[5]), rel=int(f[6]),
                    word=f[7] if len(f) > 7 else '')
    if f[0] == 'STOP':
        return dict(kind='STOP', lab=f[1], step=int(f[2]))
    if f[0] == 'BF':
        return dict(kind='BF', lab=f[1], step=int(f[2]), rel=int(f[3]), word=f[4])
    if f[0] == 'TIMEOUT':
        if len(f) > 6:
            return dict(kind='TIMEOUT', lab=f[1], step=int(f[2]), q=f[3], c=int(f[4]), rel=int(f[5]), word=f[6])
        return dict(kind='TIMEOUT', lab=f[1], step=int(f[2]))
    return dict(kind='?', line=line)


def stream(machine, jobs, maxsteps, events='-', maxrep=1):
    """generator over parsed output lines (streams while sim.exe runs)."""
    import tempfile
    fd, path = tempfile.mkstemp(suffix='.txt', dir=os.path.join(HERE, 'tmp'))
    with os.fdopen(fd, 'w') as f:
        for lab, w, h, q in jobs:
            f.write('%s %s %d %s\n' % (lab, w, h, q))
    p = subprocess.Popen([SIM, machine, path, str(maxsteps), events, str(maxrep)], stdout=subprocess.PIPE, text=True,
                         creationflags=IDLE, bufsize=1)
    try:
        for line in p.stdout:
            yield parse(line)
    finally:
        p.wait()
        os.remove(path)


def show(x):
    if x['kind'] in ('EV', 'HALT') or (x['kind'] == 'TIMEOUT' and 'word' in x):
        it, idx, off = tokpos(x['word'], x['rel'])
        return '%s %s %d %s%d h%d.%d | %s [[ %s ]] %s' % (x['lab'], x.get('n', x['kind']), x['step'], x['q'], x['c'], idx,
                                                       off, fmt(it[:idx]), fmt(it[idx:idx + 1]), fmt(it[idx + 1:]))
    return str(x)


def bword(ts, A):
    """B-form [t1..tn | A]: tape D(t1)..D(tn) D0 D(A), head on the blank right of it, state G."""
    w = ''.join(D(t) for t in ts) + D(0) + D(A)
    return w, len(w), 'G'


def bparse(word, rel):
    """if the word (head at rel, on the right edge) is B-form, return (list, A) else None."""
    if rel != len(word):
        # head must be on the first blank right of the word
        if not (rel == len(word) - 1 and word[-1] == '0'):
            return None
        word = word[:-1]
    it = tok(word)
    if len(it) < 2 or any(not isinstance(x, int) for x in it) or it[-2] != 0:
        return None
    return it[:-2], it[-1]


class Server:
    """persistent sim.exe reading jobs from stdin (Idle priority)."""

    def __init__(self, machine=M10, events='Bf,E0', maxrep=10 ** 9, maxsteps=10 ** 10):
        self.p = subprocess.Popen([SIM, machine, '-', str(maxsteps), events, str(maxrep)], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True, creationflags=IDLE, bufsize=1)
        self.k = 0

    def job(self, w, h, q, maxsteps=None):
        self.k += 1
        lab = 'j%d' % self.k
        self.p.stdin.write('%s %s %d %s%s\n' % (lab, w, h, q, '' if maxsteps is None else ' %d' % maxsteps))
        self.p.stdin.flush()
        out = []
        for line in self.p.stdout:
            if line.startswith('END '):
                return out
            out.append(parse(line))
        raise RuntimeError('sim server died')

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=5)
        except Exception:
            self.p.kill()
