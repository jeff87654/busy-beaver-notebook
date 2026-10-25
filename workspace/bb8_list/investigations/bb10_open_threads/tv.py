"""Token view of a literal run from a configuration written in the follower's symbolic notation.
  python tv.py MACHINE "CONFIG" "b=6,R2=200" MAXSTEPS [hyb options, e.g. -k 2 -q B -m 400]
CONFIG: D(expr)[^{expr}]  (pat)^expr / c^expr runs  <junk>  ( ... )^{expr} blocks  [Q] marks the head (state Q);
without [Q] the head is on the blank right of the word in state B.  '|' and 'tail' are ignored.
Output: hyb lines with item lists compressed into repeated blocks (follow2.compress).  Fails loudly on bad input."""
import os, re, subprocess, sys, tempfile
from fractions import Fraction
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'bb10_bb7_descendants'))
import follow2 as F2  # noqa: E402

HYB = str(HERE / os.environ.get('HYBX', 'hyb.exe'))
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
TMP = Path(os.environ.get('CLAUDE_JOB_DIR', tempfile.gettempdir())) / 'tmp'
TMP.mkdir(parents=True, exist_ok=True)


def ev(expr, vals):
    e = re.sub(r'(?<![A-Za-z_\d])(\d+)', r'F(\1)', expr)
    x = eval(e, {'F': Fraction, '__builtins__': {}}, {k: Fraction(v) for k, v in vals.items()})
    if Fraction(x).denominator != 1:
        raise ValueError(f'non-integer {expr} = {x} at {vals}')
    return int(x)


def build(s, vals):
    """returns (word, head index or None, state or None)"""
    s = s.replace('|', ' ').replace('tail', ' ')
    pos = 0
    head = [None, None]

    def seq(end):
        nonlocal pos
        out = ''
        while True:
            while pos < len(s) and s[pos] == ' ':
                pos += 1
            if pos >= len(s):
                if end:
                    raise ValueError('unclosed (')
                return out
            if s[pos] == ')':
                if not end:
                    raise ValueError(f'stray ) at {pos}')
                pos += 1
                return out
            out += item(out)

    def count():
        nonlocal pos
        if s.startswith('^{', pos):
            j = s.index('}', pos)
            c = ev(s[pos + 2:j], vals); pos = j + 1; return c
        if s.startswith('^', pos):
            m = re.compile(r'\^(\d+)').match(s, pos)
            pos = m.end(); return int(m.group(1))
        return 1

    def item(sofar):
        nonlocal pos
        m = re.compile(r'D\(([^)]*)\)').match(s, pos)
        if m:
            pos = m.end(); v = ev(m.group(1), vals)
            if v < 0:
                raise ValueError(f'negative token {m.group(1)}')
            c = count()
            if c < 0:
                raise ValueError('negative count')
            return ('10' * v + '1') * c
        m = re.compile(r'\((10|01)\)\^(\{[^}]*\}|\d+)').match(s, pos)
        if m:
            pos = m.end(); k = m.group(2)
            return m.group(1) * (ev(k[1:-1], vals) if k.startswith('{') else int(k))
        m = re.compile(r'([01])\^(\{[^}]*\}|\d+)').match(s, pos)
        if m:
            pos = m.end(); k = m.group(2)
            return m.group(1) * (ev(k[1:-1], vals) if k.startswith('{') else int(k))
        m = re.compile(r'\[([A-P])\]').match(s, pos)
        if m:
            pos = m.end(); head[0] = len(prefix_len[0]) if False else None
            head[1] = m.group(1); head[0] = ('MARK',)
            return '\x00'
        if s[pos] == '<':
            j = s.index('>', pos)
            ent = F2.parse_items(s[pos:j + 1]); pos = j + 1
            m2 = re.compile(r'\*(\d+)').match(s, pos)
            c = 1
            if m2:
                pos = m2.end(); c = int(m2.group(1))
            return F2.word_of(ent) * c
        if s[pos] == '(':
            pos += 1
            inner = seq(True)
            return inner * count()
        m = re.compile(r'(\d+)(?:\*(\d+))?').match(s, pos)
        if m:   # bare hyb token "m" or "m*k"
            pos = m.end()
            return ('10' * int(m.group(1)) + '1') * int(m.group(2) or 1)
        raise ValueError(f'cannot parse at {pos}: {s[pos:pos + 30]!r}')

    prefix_len = ['']
    w = seq(False)
    if '\x00' in w:
        h = w.index('\x00'); w = w.replace('\x00', '')
        return w, h, head[1]
    return w, None, None


def pretty(items_str):
    try:
        ent = F2.parse_items(items_str.replace('[', '<[').replace(']', ']>') if False else items_str)
    except Exception:
        return items_str
    try:
        return F2.fmt_sym(F2.symc(F2.compress(ent)))
    except Exception:
        return items_str


def run(machine, cfg, vals, maxsteps, opts, raw=False):
    """yields output lines as they come (streaming)"""
    w, h, q = build(cfg, vals)
    fd, path = tempfile.mkstemp(suffix='.txt', dir=TMP)
    with os.fdopen(fd, 'w') as f:
        f.write(w)
    p = subprocess.Popen([HYB, machine, path, str(len(w) if h is None else h), q or 'B', str(maxsteps), *opts],
                         stdout=subprocess.PIPE, text=True, creationflags=LOW)
    try:
        for line in p.stdout:
            line = line.rstrip(chr(10))
            if ' | ' in line and not raw:
                a, b = line.split(' | ', 1)
                if '[' not in b:
                    b = pretty(b)
                line = a + ' | ' + b
            yield line
    finally:
        p.wait()
        os.unlink(path)


if __name__ == '__main__':
    m, cfg, vs, ms = sys.argv[1:5]
    vals = dict((k, int(v)) for k, v in (p.split('=') for p in vs.split(',') if p))
    raw = '--raw' in sys.argv
    opts = [o for o in sys.argv[5:] if o != '--raw']
    for line in run(m, cfg, vals, int(ms), opts, raw):
        print(line, flush=True)
