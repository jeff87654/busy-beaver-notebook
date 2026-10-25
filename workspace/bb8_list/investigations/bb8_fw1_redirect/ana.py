"""ana.py FILES...: classify henum leaves whose blank run is engine-like (T) by their exhaustion map.
E-map columns = A in AS. Phi = a + sum(ds) mod 2 (F1/F2 invariant, valid when D/Bk are the base's).
Chain: start parity p0 (base's real E parity), apply E-map per parity; report #rebuilds before halt."""
import sys, re, os, collections
AS = [1, 2, 3, 4, 5, 6, 7, 8, 15, 16]
P0 = {'u': 0, 't': 0, 'b': 1, 'c': 1, 'j': 1, 'i': 0, 'a': 0, 'r': 0, 's': 0, 'h': 0}
def expand(s):
    out = []
    for x in s.split(','):
        if not x: continue
        if '^' in x: v, n = x.split('^'); out += [int(v)] * int(n)
        else: out.append(int(x))
    return out
def parse_out(x):
    if x.startswith('K:'):
        _, k, st = x.split(':'); ds, a, b = k.split(';'); return ('K', expand(ds), int(a), int(b))
    if x.startswith('H:'): return ('H',)
    return (x[0],)
def classify(tag, cols):
    em = {A: parse_out(c) for A, c in zip(AS, cols)}
    per = {}
    for p in (0, 1):
        outs = [em[A] for A in AS if A % 2 == p]
        kinds = set(o[0] for o in outs)
        if kinds == {'H'}: per[p] = 'H'
        elif kinds == {'K'}:
            ph = set((o[2] + sum(o[1])) % 2 for o in outs)
            lens = [len(o[1]) for o in outs]
            grow = lens[-1] > lens[0] + 3
            zero = any(0 in o[1] for o in outs)
            per[p] = ('K', ph.pop() if len(ph) == 1 else 'mixed', grow, zero)
        else: per[p] = ''.join(sorted(kinds))
    return em, per
def chain(per, p0):
    seq = []; p = p0; seen = set()
    while True:
        if p in seen: seq.append('loop'); break
        seen.add(p); o = per[p]
        if o == 'H': seq.append('H'); break
        if not isinstance(o, tuple): seq.append('?' + o); break
        if o[1] == 'mixed': seq.append('Rmixed'); break
        seq.append('R' + ('g' if o[2] else 'f')); p = o[1]
    return seq
if __name__ == '__main__':
    summ = collections.Counter(); keep = []
    for fn in sys.argv[1:]:
        tag = os.path.basename(fn)[2]
        for l in open(fn):
            f = l.rstrip('\n').split('\t')
            if l.startswith('#') or len(f) < 3: continue
            st = f[2][0]
            if st != 'T': summ[(tag, 'blank' + st)] += 1; continue
            em, per = classify(tag, f[3:])
            ch = chain(per, P0.get(tag, 0))
            key = ' '.join(ch); summ[(tag, key)] += 1
            if ch[-1] == 'H' and len(ch) >= 2 or any(c.startswith('?') for c in ch) or 'Rmixed' in ch: keep.append((tag, f[0], f[1], key, per))
    for k, v in sorted(summ.items()): print(k[0], f'{v:6d}', k[1])
    print('--- kept', len(keep))
    for x in keep[:4000]: print(*x[:4], x[4], sep='\t')
