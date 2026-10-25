"""collapse2.py: generic sound state-elimination for 2-symbol TMs (syntactic, no invariants).
(1) MERGE: partition refinement (bisimulation) -- states with identical transitions modulo the partition are merged.
(2) GADGET: for a set G of non-start states (all singles and pairs), every transition entering G from outside,
    (S,c) -> (w,d,X), is symbolically executed from the entry (cell p = w known, every other cell an unknown symbol that is
    branched on when read) until the head is at p-1 or p+1 in a state outside G with every cell except p back to its
    original content.  If all branches end with the same (cell p value y, side, state Z) within MAXS steps, and no
    branch reads an undefined transition, the entry is replaced by (S,c) -> (y, side, Z).  If every entry is replaced,
    G is unreachable and is removed.  Each step of the reduced machine is a fixed macro of the original on every tape,
    so the two machines halt together with identical tapes.
Iterated until nothing applies.
usage: python collapse2.py [--maxs N] [--pairs] FILE_OR_MACHINE...   (file lines: machine first token)"""
import sys, os, itertools
MAXS = 40
def parse(m):
    rows = m.split('_'); n = len(rows); T = []
    for p in rows:
        row = []
        for c in range(2):
            t = p[3 * c:3 * c + 3]
            row.append(None if (t[0] == '-' or t[2] in 'Z-' or ord(t[2]) - 65 >= n) else (int(t[0]), 1 if t[1] == 'R' else -1, ord(t[2]) - 65))
        T.append(row)
    return T
def fmt(T):
    return '_'.join(''.join('---' if t is None else '%d%s%s' % (t[0], 'R' if t[1] > 0 else 'L', chr(65 + t[2])) for t in row) for row in T)
def renumber(T, keep):
    ren = {o: i for i, o in enumerate(keep)}
    return [[None if t is None else (t[0], t[1], ren[t[2]]) for t in T[o]] for o in keep]
def merge(T):
    n = len(T); part = [0] * n
    while True:
        sig = [tuple(None if t is None else (t[0], t[1], part[t[2]]) for t in T[s]) for s in range(n)]
        key = {}; new = []
        for s in range(n):
            k = (part[s], sig[s]); key.setdefault(k, len(key)); new.append(key[k])
        if len(set(new)) == len(set(part)): break
        part = new
    if len(set(part)) == n: return None
    rep = {}
    for s in range(n): rep.setdefault(part[s], s)
    keep = sorted(rep.values()); ren = {s: rep[part[s]] for s in range(n)}
    U = [[None if t is None else (t[0], t[1], ren[t[2]]) for t in T[s]] for s in range(n)]
    return renumber(U, keep), [s for s in range(n) if s not in keep]
def run_entry(T, G, w, d, X):
    """symbolic execution; returns the common net (y, side, Z) or None"""
    results = set()
    stack = [({0: w}, {}, d, X, 0)]   # written cells, assumptions on original cells, head, state, steps
    while stack:
        tape, asm, h, q, k = stack.pop()
        while True:
            if q not in G and h in (-1, 1):
                ok = True
                for c, v in tape.items():
                    if c != 0 and (c not in asm or asm[c] != v): ok = False; break
                if ok: results.add((tape[0], h, q)); break
            if k >= MAXS: return None
            if h in tape: s = tape[h]
            elif h in asm: s = asm[h]
            else:
                a2 = dict(asm); a2[h] = 1; stack.append((dict(tape), a2, h, q, k))
                asm = dict(asm); asm[h] = 0; s = 0
            tr = T[q][s]
            if tr is None: return None
            tape = dict(tape); tape[h] = tr[0]; h += tr[1]; q = tr[2]; k += 1
        if len(results) > 1: return None
    return results.pop() if len(results) == 1 else None
def gadget(T, G):
    n = len(T)
    if 0 in G: return None
    ent = [(s, c) for s in range(n) if s not in G for c in range(2) if T[s][c] is not None and T[s][c][2] in G]
    if not ent: return None
    U = [list(r) for r in T]
    for s, c in ent:
        w, d, X = T[s][c]; r = run_entry(T, G, w, d, X)
        if r is None: return None
        U[s][c] = r
    # G must now be unreachable from outside
    for s in range(n):
        if s in G: continue
        for t in U[s]:
            if t is not None and t[2] in G: return None
    keep = [i for i in range(n) if i not in G]
    return renumber(U, keep)
def collapse(m, pairs):
    T = parse(m); hist = []
    while True:
        r = merge(T)
        if r: T, gone = r; hist.append('MERGE' + ''.join(chr(65 + g) for g in gone)); continue
        n = len(T); done = False
        sets = [(g,) for g in range(1, n)] + (list(itertools.combinations(range(1, n), 2)) if pairs else [])
        for G in sets:
            V = gadget(T, set(G))
            if V is not None:
                hist.append('GADGET' + ''.join(chr(65 + g) for g in G)); T = V; done = True; break
        if not done: return T, hist
args = sys.argv[1:]; pairs = False; ms = []
i = 0
while i < len(args):
    a = args[i]
    if a == '--maxs': MAXS = int(args[i + 1]); i += 2; continue
    if a == '--pairs': pairs = True; i += 1; continue
    if os.path.exists(a): ms += [l.split()[0] for l in open(a) if l.strip() and not l.startswith('#')]
    else: ms.append(a)
    i += 1
cnt = 0
for m in ms:
    try: T, h = collapse(m, pairs)
    except Exception as e: print('ERR', m, e); continue
    cnt += 1
    if h: print('%s -> %s  (%d -> %d states: %s)' % (m, fmt(T), m.count('_') + 1, len(T), ' '.join(h)), flush=True)
print('# checked', cnt, file=sys.stderr)
