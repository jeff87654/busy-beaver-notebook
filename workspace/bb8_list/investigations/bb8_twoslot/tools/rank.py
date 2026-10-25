"""rank.py TSV [TSV...] : classify wtree rows by escalation count (W2 skeleton) and outcome.
Escalation = a clear of depth k >= KESC whose k exceeds the previous clear's depth by >= DK (a list rebuilt from an
accumulator).  M8 in W2: 11 817 168 12 753 445x151 -> 2 escalations, HALT.
Prints counts per (outcome class, #esc) and the rows with >= MINESC escalations (halting first)."""
import sys, collections, os
KESC = int(os.environ.get('KESC', '300')); DK = int(os.environ.get('DK', '100')); MINESC = int(os.environ.get('MINESC', '2'))
def ks(z):
    out = []
    for t in z.split():
        if t == '...': out.append(None); continue
        if 'x' in t: a, c = t.split('x'); out += [int(a)] * min(int(c), 3)
        else:
            try: out.append(int(t))
            except ValueError: pass
    return out
def nesc(z):
    e = 0; prev = None
    for k in ks(z):
        if k is None: prev = None; continue
        if prev is not None and k >= KESC and k >= prev + DK: e += 1
        prev = k
    return e
rows = []
for f in sys.argv[1:]:
    for l in open(f):
        p = l.rstrip('\n').split('\t')
        if len(p) < 9: continue
        out = p[2].replace('@lazy', '')
        cls = 'HALT' if out.startswith('HALT') else out.split('_')[0] if '_' in out else out
        rows.append((p[0], p[1], out, cls, nesc(p[8]), p[8], p[4]))
c = collections.Counter((r[3], r[4]) for r in rows)
for k in sorted(c): print(k, c[k])
print('--- rows with >= %d escalations' % MINESC)
for r in sorted(rows, key=lambda r: (r[3] != 'HALT', -r[4])):
    if r[4] >= MINESC: print(r[0], r[1], r[2], 'esc=%d' % r[4], 'ones=' + r[6], r[5][:150])
