"""Concrete tapes of the BB(9) record's late configurations, parsed from the Coq files (no hand transcription).

  c_end(q, r)       : the halting configuration (BB9_record_bound.v, Definition c_end), state I reading 1.
  d2start(q, b)     : Kg (0^(5q+11)) [2;4;21;4] 0 b 6 = Kt (1^(5q+11) ++ [2;4;21;4]) 1 (3b+2) 6, state B (D2STAGE input).
  Kt(ds, m, r, t)   : 0^inf 11 D(d_n)..D(d_1) D(m) (10)^r 11 (11111100)^t 1001 B> 0^inf  (ds nearest-first).
A config is (tape string of '0'/'1', head index, state letter); the tape is padded with PAD zeros on each side.
"""
import re
from pathlib import Path

PROOFS = Path(__file__).resolve().parents[2] / 'proofs'
PAD = 40


def _side(expr, params):
    """busycoq side expression 'x >> y >> [..]^^p *> ... >> const 0' -> list of symbols (head-adjacent first)"""
    expr = expr.strip()
    if expr.startswith('(') and expr.endswith(')'):
        expr = expr[1:-1].strip()
    out = []
    pos = 0
    tok = re.compile(r'\s*(?:(const 0)|([01])\s*>>|\[([01;]*)\]\^\^(\w+)\s*\*>)')
    while pos < len(expr):
        m = tok.match(expr, pos)
        if not m:
            raise ValueError(f'cannot parse side at {expr[pos:pos+60]!r}')
        if m.group(1):
            pos = m.end()
            if expr[pos:].strip():
                raise ValueError('text after const 0')
            return out
        if m.group(2):
            out.append(m.group(2))
        else:
            blk = m.group(3).split(';')
            n = params[m.group(4)] if not m.group(4).isdigit() else int(m.group(4))
            out += blk * n
        pos = m.end()
    raise ValueError('side without const 0')


def _config(text, params):
    """'(L) <{{S}} (R)' or '(L) {{S}}> (R)' -> (tape, head, state)"""
    m = re.fullmatch(r'\s*(\(.*\)|const 0)\s*(<\{\{(\w)\}\}|\{\{(\w)\}\}>)\s*(\(.*\)|const 0)\s*', text, re.S)
    if not m:
        raise ValueError('not a config')
    L, R = _side(m.group(1), params), _side(m.group(5), params)
    if m.group(3):                         # l <{{S}} r : head reads hd l
        st = m.group(3)
        head_sym, left = L[0], L[1:]
        right = R
    else:                                  # l {{S}}> r : head reads hd r
        st = m.group(4)
        left = L
        head_sym, right = (R[0], R[1:]) if R else ('0', [])
    tape = '0' * PAD + ''.join(reversed(left)) + head_sym + ''.join(right) + '0' * PAD
    return tape, PAD + len(left), st


_CEND = None


def c_end(q, r):
    global _CEND
    if _CEND is None:
        src = (PROOFS / 'BB9_record_bound.v').read_text()
        m = re.search(r'Definition c_end \(q r : nat\) : Q \* tape :=(.*?)\.\n', src, re.S)
        _CEND = m.group(1)
    return _config(_CEND, {'q': q, 'r': r})


def lft(ds):
    out = []
    for d in ds:
        out += ['1'] + ['0', '1'] * d
    return out + ['1', '1']


def Kt(ds, m, r, t):
    left = ['1', '0', '0', '1'] + ['0', '0', '1', '1', '1', '1', '1', '1'] * t + ['1', '1'] + ['0', '1'] * r + \
           ['1'] + ['0', '1'] * m + lft(ds)
    tape = '0' * PAD + ''.join(reversed(left)) + '0' + '0' * PAD
    return tape, PAD + len(left), 'B'


def d2start(q, b):
    return Kt([1] * (5 * q + 11) + [2, 4, 21, 4], 1, 3 * b + 2, 6)


def ones(tape):
    return tape.count('1')


if __name__ == '__main__':
    t, h, s = c_end(0, 0)
    print(s, h, t[PAD:h], '[' + t[h] + ']', t[h + 1:].rstrip('0'))
