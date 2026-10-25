"""symchk.py : sound symbolic measurement of F89 odd-mode rules with never_audit symsim.
Original orientation: K-config = [D on blank] 0 0 [1 (01)^d1][1 (01)^d2]...[1 (01)^dn], right of it blank.
Mirrored machine (right-handed): tape = (10)^dn 1 ... (10)^d1 1 0 0 D>.
Digit entries: int, or ('H', r) fresh symbol (residue r mod mg, lower bound hlb), or ('H', r, c) = symbol + c,
or ('Z', 'H') = symbolic number of 1-digits (block '101'^H)."""
import sys, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\never_audit')
from sym import mirror, parse_tape, Lin
SYMSIM = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\never_audit\src\symsim.exe'
M = '1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE'
MM = mirror(M)

def encode(digs):
    """returns symsim token string (mirrored) and list of symbol names in creation order"""
    toks = []; names = []
    for e in reversed(digs):      # top digit first (leftmost in mirrored)
        if isinstance(e, int):
            if e: toks.append('10^%d' % e)
            toks.append('1')
        elif e[0] == 'H':
            toks.append('10^H%d' % e[1]);
            if len(e) > 2 and e[2]: toks.append('10^%d' % e[2])
            toks.append('1')
        elif e[0] == 'Z':
            toks.append('101^H%d' % e[1])
    toks.append('0 0 D>')
    return ' '.join(toks)

def symnames(digs):
    # symsim creates symbols in token order (mirrored order)
    n = 0; out = {}
    for i, e in enumerate(reversed(digs)):
        if not isinstance(e, int): out[len(digs) - 1 - i] = 'X%d' % n; n += 1
    return out

def decode(tp):
    """symsim STOP tape (mirrored, head at right end) -> ('p1', digits) or ('other', raw)"""
    items, q, h = parse_tape(tp)
    left = items[:h]
    if any(w.strip('0') for w, n in items[h:]): return 'other', 'right nonblank'
    # original orientation: reverse
    st = []
    for w, n in reversed(left):
        w = w[::-1]
        if n.isconst():
            st.extend(w * int(n.const()))
        else:
            st.append(('blk', w, n))
    # strip leading zeros, count them
    i = 0; z = 0
    while i < len(st) and st[i] == '0': i += 1; z += 1
    st = st[i:]
    # strip trailing zeros
    while st and st[-1] == '0': st.pop()
    if z != 2: return 'other', 'lead zeros %d' % z
    digs = []; cur = None; pos = 0
    def rot(b):
        _, w, n = b
        return [w[0], ('blk', w[1:] + w[0], n - 1)] + list(w[1:])
    while pos < len(st):
        x = st[pos]
        if isinstance(x, tuple):
            w = x[1]
            if w == '01' and cur is not None: cur = cur + x[2]; pos += 1; continue
            if w == '101':
                if cur is not None: digs.append(cur)
                digs.append(('Z', x[2] - 1)); cur = Lin.c(1); pos += 1; continue
            # rotate
            st[pos:pos + 1] = rot(x); continue
        if x == '1':
            if cur is not None: digs.append(cur)
            cur = Lin.c(0); pos += 1; continue
        # x == '0': need next '1' as unit
        if cur is None: return 'other', 'zero before first digit'
        nxt = st[pos + 1] if pos + 1 < len(st) else None
        if nxt == '1': cur = cur + 1; pos += 2; continue
        if isinstance(nxt, tuple):
            st[pos + 1:pos + 2] = rot(nxt); continue
        return 'other', 'double zero'
    if cur is not None: digs.append(cur)
    # merge: flatten ints
    out = []
    for d in digs:
        if isinstance(d, tuple):
            if not (d[1].isconst() and d[1].const() == 0): out.append(d)
        else: out.append(d)
    return 'p1', out

def run(digs, nstop=40, mg=2, hlb=int(__import__("os").environ.get("HLB","5")), budget=200000, tl=30):
    inp = '%s D %s\n' % (MM, encode(digs))
    args = [SYMSIM, 'run', '--noch', '--nokt', '--mg', str(mg), '--hlb', str(hlb), '--budget', str(budget),
            '--tapeall', '200000', '--stopq', 'D', '--stopn', str(nstop), '--stopall', '--tlimit', str(tl)]
    p = subprocess.run(args, input=inp, capture_output=True, text=True, timeout=tl * 3 + 30)
    res = []; verdict = None
    for l in p.stdout.splitlines():
        if l.startswith('STOP '):
            a, b = l.split(' TAPE ', 1); tp = b.rsplit(' |', 1)[0] if ' |' in b else b
            res.append(tp.strip())
        elif l.startswith('R '): verdict = ' '.join(l.split()[3:5])
    return res, verdict, p.stdout

def first_p1(digs, **kw):
    res, verdict, raw = run(digs, **kw)
    for tp in res:
        k, d = decode(tp)
        if k == 'p1': return d, verdict
    return None, (verdict, res[:3])

def norm(d):
    """digits -> canonical list: ints/Lin as Lin; Z blocks kept"""
    out = []
    for e in d:
        if isinstance(e, tuple) and e[0] == 'Z': out.append(('Z', e[1] if isinstance(e[1], Lin) else Lin.c(e[1])))
        else: out.append(e if isinstance(e, Lin) else Lin.c(e))
    # expand constant Z blocks into 1s; merge adjacent
    o2 = []
    for e in out:
        if isinstance(e, tuple) and e[1].isconst(): o2 += [Lin.c(1)] * int(e[1].const())
        else: o2.append(e)
    return o2

def show(d):
    return '[' + ', '.join(('1^{%r}' % e[1]) if isinstance(e, tuple) else repr(e) for e in d) + ']'
if __name__ == '__main__':
    d, v = first_p1([('H', 1), ('H', 1, 2), ('H', 1)])
    print(show(d), v)
