"""Extract stage rewrites from a ghf.py -v log: event config (after a jump) -> the K-config where the next jump starts."""
import sys, re
def unrle(s):
    out = []
    for tok in s.split():
        m = re.match(r'^(H\[\d+\]|\d+)(?:\^(\d+))?$', tok)
        if not m: raise ValueError(tok)
        v = m.group(1); c = int(m.group(2) or 1)
        out += [v] * c
    return out
def stages(fn):
    lines = open(fn).read().splitlines()
    ev = None; last = None; out = []
    for l in lines:
        if l.startswith('J'):
            m = re.match(r'^J(\d+) (\S+) huge=(\d) steps=(\d+) cleared=(\d+) \| (.*?) \|\| zeros=(\d+) r=(\S+)$', l)
            n, kind, _, _, _, left, z, r = m.groups()
            if ev is not None and last is not None: out.append((ev, last))
            ev = (int(n), kind, unrle(left), int(z), r); last = None
        elif l.startswith('  L'):
            m = re.match(r'^  L (\d+) -> (.*)$', l); last = unrle(m.group(2))
        elif l.startswith('HALT'):
            out.append((ev, ('HALT', l)))
    return out
def diff(ev, cfg):
    n, kind, left, z, r = ev
    full = left + ['1'] * z + ['1', r]
    if cfg[0] == 'HALT': return f'J{n} {kind} ...{" ".join(left[-6:])} z={z} -> {cfg[1]}'
    p = 0
    while p < min(len(full), len(cfg)) and full[p] == cfg[p]: p += 1
    p = min(p, len(left) - 1)
    # strip common trailing zeros
    a, b = full[p:], cfg[p:]
    za = 0
    while a and a[-3 - za:] and False: pass
    def comp(x):
        o = []
        for t in x:
            if o and o[-1][0] == t: o[-1][1] += 1
            else: o.append([t, 1])
        return ' '.join(t if c == 1 else f'{t}^{c}' for t, c in o)
    return f'J{n} {kind} keep={p} [{comp(a)}] -> [{comp(b)}]'
if __name__ == '__main__':
    for ev, cfg in stages(sys.argv[1]): print(diff(ev, cfg))
