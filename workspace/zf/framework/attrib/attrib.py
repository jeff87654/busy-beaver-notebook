"""Attribute the states of Wade's zf2.tm (393 = 69 framework + 324 DAG) to framework roles and program subroutines.
Usage: python -I attrib.py   -> prints summary JSON, dumps attrib_nodes.tsv / attrib_summary.json / rebuilt.tm here."""
import sys, os, json
from collections import Counter, defaultdict
from functools import lru_cache
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
import zf2, tmsim
ORDER = [16, 17, 3, 18, 4, 7, 8, 9, 11, 5, 12, 13, 14, 2, 15, 0, 1, 6, 10, 19]
CLAUSES = ["DET","GEN","B1","B2","B3","B4","B6b","B8b","B6a","B6b#2","B6c","B7","B8a","B8b#2","B8c","EXT","REP","POW","UNI","INF"]
ORIG = os.path.join(HERE, '..', '..', 'ext', 'turing_machine_explorer', 'zf2.tm')

def new():
    z = zf2.ZF2(); z.debug = False; z.AXIOMORDER = ORDER; return z

# ---------------- build with snapshots ----------------
z = new()
z.main()
nb = len(z.sequences)
root_name = {}
for key, rv in z.memo.items():
    if rv == (): continue
    i = z.add_sequence(rv)
    if not isinstance(i, int): continue
    def atom(x):
        if x.startswith('3.'):
            r, op = x[2:].rsplit('.', 1); return r + ('+' if op == 'inc' else '-')
        return x.lstrip('_')
    def ra(a):
        if isinstance(a, int):
            s = z.sequences[a].seq
            if all(isinstance(x, str) for x in s): return '[' + ' '.join(atom(x) for x in s) + ']'
            return f'#{a}'
        if a == (): return '[]'
        return atom(a)
    nm = f"{key[0]}({','.join(ra(a) for a in key[1:])})"
    root_name.setdefault(i, nm)
assert len(z.sequences) == nb
main_i = z.find_seq("main().0")
main_orig = z.sequences[main_i].seq
pre_seqs = {i: s.seq for i, s in enumerate(z.sequences)}

def leafkind(v):
    if v.startswith('3.'): return 'op.' + v.split('.')[-1]
    if v.startswith('_break'): return 'break'
    if v.startswith('_continue'): return 'continue'
    return v
@lru_cache(None)
def inl(i):
    c = Counter()
    for v in pre_seqs[i]:
        if isinstance(v, int): c += inl(v)
        else: c[leafkind(v)] += 1
    return c
@lru_cache(None)
def calls_in(i):
    c = Counter()
    if i in root_name: c[root_name[i]] += 1
    for v in pre_seqs[i]:
        if isinstance(v, int): c += calls_in(v)
    return c
inlined = inl(main_i)
inlined_calls = calls_in(main_i)
# pre-outlining reachable sequences and their total length
def reach_pre():
    seen = set(); st = [main_i]
    while st:
        i = st.pop()
        if i in seen: continue
        seen.add(i); st += [v for v in pre_seqs[i] if isinstance(v, int)]
    return seen
rp = reach_pre()
pre_cells_naive = sum(len(pre_seqs[i]) - 1 for i in rp)  # cons cells if each reachable sequence reduced without suffix sharing

# ---- main sections ----
AX = z.axioms(); assert len(z.sequences) == nb
def nonempty(lst): return [x for x in (z.add_sequence(e) for e in lst) if x != ()]
sec = []
pre = len(main_orig) - 1 - sum(len(nonempty(AX[i])) for i in ORDER)
assert pre == 18, pre
for k in range(pre):
    sec.append('main:if_not_decnz(prooflist)' if k == 0 else 'main:decode' if k < 17 else 'main:default v_0')
for i in ORDER:
    sec += ['main:' + CLAUSES[i]] * len(nonempty(AX[i]))
sec.append('main:final-check')
assert len(sec) == len(main_orig)
clause_len = {CLAUSES[i]: len(nonempty(AX[i])) for i in ORDER}
@lru_cache(None)
def inl_list(v):
    return inl(v) if isinstance(v, int) else Counter({leafkind(v): 1})
clause_inlined_ops = {}
for k, v in enumerate(main_orig):
    c = inl_list(v); s = sec[k]
    clause_inlined_ops[s] = clause_inlined_ops.get(s, 0) + c['op.inc'] + c['op.decnz']

# ---- outline ----
z.breakout_common_subsequences()
def explen(v):
    if not isinstance(v, int) or v < nb: return 1
    return sum(explen(w) for w in z.sequences[v].seq)
main_out = z.sequences[main_i].seq
spans, pos = [], 0
for v in main_out:
    L = explen(v); spans.append(set(sec[pos:pos+L])); pos += L
assert pos == len(main_orig)
outlined_new = [i for i in z.reachable() if i >= nb]
outlined_desc = []
for i in outlined_new:
    outlined_desc.append((i, len(z.sequences[i].seq), explen(i)))
z.reduce_to_cons(); z.name_sequences(); z.generate(); z.tm.gc(); z.tm.statename = z.tm.start
z.tm.save('rebuilt.tm')
s1, t1 = tmsim.load('rebuilt.tm'); s2, t2 = tmsim.load(ORIG)
assert s1 == s2 and t1 == t2, 'rebuild differs from zf2.tm'
states = sorted({s for s, _ in t1})
assert len(states) == 393

# ---------------- framework ----------------
fw = [s for s in states if s[0].isdigit()]
def fwrole(s):
    if s.startswith('0.boot'): return 'boot (const)'
    if s.startswith('1.inc'): return '1.inc* (const)'
    if s.startswith('1.decnz'): return '1.decnz* (const)'
    if s.startswith('1.sel'): return '1.sel* (const)'
    if s.startswith('2.ret'): return '2.ret* (const)'
    if s.startswith('3.'): return '3.<reg>.inc/decnz (per register)'
    if s in ('4.dispatch.1', '5.root'): return 'dispatch.1 + 5.root (const)'
    if s.startswith('4.dispatch'): return '4.dispatch.2..Z (Z=max car-run)'
    if s.startswith('6.break'): return '6.break.k'
    if s.startswith('6.continue'): return '6.continue.k'
fwc = Counter(fwrole(s) for s in fw)

# ---------------- DAG attribution ----------------
seqs = z.sequences
reach = list(z.reachable())
assert len(reach) == 324 and all(len(seqs[i].seq) == 2 for i in reach)
name = {i: seqs[i].name for i in reach}
assert set(name.values()) == {s for s in states if not s[0].isdigit()}
spine = []; cur = main_i
for k in range(len(main_out) - 1):
    spine.append(cur); nxt = seqs[cur].seq[1]
    if k < len(main_out) - 2: cur = nxt
spine_k = {}
for k, n in enumerate(spine):
    assert n not in spine_k; spine_k[n] = k
children = {i: [v for v in seqs[i].seq if isinstance(v, int)] for i in reach}
def own(i):
    if i in spine_k: return set(spans[spine_k[i]])
    if i in root_name and i != main_i: return {root_name[i]}
    return None
ctx = defaultdict(set)
for i in reach:
    o = own(i)
    if o: ctx[i] |= o
changed = True
while changed:
    changed = False
    for i in reach:
        for side, c in enumerate(seqs[i].seq):
            if not isinstance(c, int) or own(c) is not None: continue
            if i in spine_k:
                k = spine_k[i]
                add = spans[k] if side == 0 else (spans[k+1] if k == len(spine) - 1 else set())
            else:
                add = ctx[i]
            if not add <= ctx[c]:
                ctx[c] |= add; changed = True
assert all(ctx[i] for i in reach)
# root nodes that are ALSO reached as a non-root descendant / other contexts: record in-edge contexts
order = []; seen = set()
def visit(i):
    if i in seen: return
    seen.add(i); order.append(i)
    for c in children[i]: visit(c)
sys.setrecursionlimit(10000); visit(main_i)
secorder = list(dict.fromkeys(sec))

def family(nm):
    if nm.startswith('main:'):
        s = nm[5:]
        return 'main: clause ' + s if s.split('#')[0] in CLAUSES else 'main: ' + s
    f = nm.split('(')[0]
    if f == 'while_decnz':
        body = nm[len('while_decnz('):-1].split(',', 1)[1]
        n_inc = body.count('+')
        return {0: 'while_decnz clear', 1: 'while_decnz move', 2: 'while_decnz copy2'}.get(n_inc, 'while_decnz other')
    return f
def primary(i):
    c = ctx[i]
    if len(c) == 1: return next(iter(c))
    subs = sorted(x for x in c if not x.startswith('main:'))
    if subs: return subs[0]
    return min(c, key=secorder.index)

rows = []
for i in order:
    c = sorted(ctx[i]); p = primary(i)
    rows.append((i, name[i], p, family(p), len(c), ';'.join(c), seqs[i].seq))
with open('attrib_nodes.tsv', 'w') as f:
    f.write('seq\tstate\tprimary_owner\tfamily\tn_ctx\tcontexts\tcar\tcdr\n')
    for r in rows:
        car, cdr = r[6]
        f.write('\t'.join(map(str, r[:6])) + f'\t{name.get(car, car)}\t{name.get(cdr, cdr)}\n')

fam = Counter(r[3] for r in rows)
fam_multi = Counter(r[3] for r in rows if r[4] > 1)
famset_shared = Counter('+'.join(sorted({family(x) for x in ctx[r[0]]})) for r in rows if len({family(x) for x in ctx[r[0]]}) > 1)
inst = Counter(r[2] for r in rows)

def closure(roots):
    out = set(); st = list(roots)
    while st:
        i = st.pop()
        if i in out: continue
        out.add(i); st += children[i]
    return out
def fam_roots(fn):
    return [i for i in reach if i in root_name and root_name[i].split('(')[0] == fn]
incl = {}
for fn in ['pair', 'unpair', 'if_eq', 'cons', 'pushwff', 'select', 'cparam', 'if_not_decnz', 'if_decnz',
           'weq','wel','wim','wn','wal','wex','wa','par1','par2','par3','v_1','v_2','v_3','v_4']:
    rts = fam_roots(fn); cl = closure(rts)
    excl = sum(1 for r in rows if r[3] == fn)
    incl[fn] = {'roots': [root_name[i] for i in rts], 'exclusive_primary': excl, 'inclusive_closure': len(cl)}
inedges = defaultdict(list)
for i in reach:
    for c in children[i]:
        if c in root_name: inedges[root_name[c]].append(name[i])

from dag import extract
_, _, nodes, regidx = extract(ORIG)
leafc = Counter()
for n, (a, b) in nodes.items():
    for e in (a, b):
        if e[0] != 'node': leafc[e] += 1
edgec = Counter(e[0] for n in nodes.values() for e in n)

z2 = new(); z2.main(); z2.reduce_to_cons(); z2.name_sequences(); z2.generate(); z2.tm.gc()
noout = len({s for s, _ in z2.tm.states if not s[0].isdigit()})
noout_tot = len({s for s, _ in z2.tm.states})

summary = dict(framework=dict(fwc), fw_total=len(fw), dag_total=len(reach), family=dict(sorted(fam.items(), key=lambda x: -x[1])),
               family_nodes_with_multiple_contexts=dict(fam_multi), cross_family_shared=dict(famset_shared),
               n_nodes_multi_ctx=sum(1 for r in rows if r[4] > 1),
               n_nodes_multi_family=sum(famset_shared.values()),
               instances=dict(sorted(inst.items(), key=lambda x: -x[1])), inclusive=incl, root_inedges=dict(inedges),
               inlined_main=dict(inlined), inlined_calls=dict(sorted(inlined_calls.items(), key=lambda x: -x[1])),
               leaves={str(k): v for k, v in sorted(leafc.items(), key=str)}, edge_kinds=dict(edgec),
               no_outlining_dag=noout, no_outlining_total=noout_tot,
               main_len_pre=len(main_orig), main_len_outlined=len(main_out), outlined_new_seqs=outlined_desc,
               pre_reachable_seqs=len(rp), pre_cells_naive=pre_cells_naive,
               clause_len=clause_len, clause_inlined_ops=clause_inlined_ops, regidx=regidx)
json.dump(summary, open('attrib_summary.json', 'w'), indent=1, default=str)

# ---------------- grouped report ----------------
prim = {r[0]: r[2] for r in rows}
parents = defaultdict(set)
for i in reach:
    for c in children[i]: parents[c].add(i)
memo_g = {}
rootidx = {v: k for k, v in root_name.items() if k in set(reach)}
def group(i, depth=0):
    if i in memo_g: return memo_g[i]
    f = family(prim[i])
    if f.startswith('while_decnz') and i not in root_name:
        g = group(rootidx[prim[i]]); memo_g[i] = g; return g
    if f.startswith('while_decnz') and depth < 50:
        gs = set()
        for p in parents[i]:
            if prim[p] == prim[i]: continue
            gs |= {group(p, depth + 1)}
        g = next(iter(gs)) if len(gs) == 1 else 'shared loops (>1 caller family)'
    elif f.startswith('main:') and len(ctx[i]) > 1:
        g = f'main: glue shared by {len(ctx[i])} sections'
    else:
        g = f
    memo_g[i] = g; return g
grp = Counter(group(r[0]) for r in rows)
assert sum(grp.values()) == 324
loopgroup = Counter((group(r[0]), r[3]) for r in rows if r[3].startswith('while_decnz'))
spine_by_sec = Counter('+'.join(sorted(spans[k])) for k in range(len(spine)))
main_nodes = [r for r in rows if all(c.startswith('main:') for c in ctx[r[0]])]
summary.update(groups=dict(sorted(grp.items(), key=lambda x: -x[1])), loop_groups={f'{a} | {b}': v for (a, b), v in loopgroup.items()},
               spine_cells=len(spine), spine_by_section=dict(spine_by_sec), main_only_nodes=len(main_nodes),
               main_shared_nodes=sum(1 for r in main_nodes if len(ctx[r[0]]) > 1))
json.dump(summary, open('attrib_summary.json', 'w'), indent=1, default=str)
if __name__ == '__main__':
    print(json.dumps(summary, indent=1, default=str))
if __name__ == '__main__':
    print('--- loop roots by group ---')
    for i in reach:
        if i in root_name and root_name[i].startswith('while_decnz'):
            n = sum(1 for r in rows if r[2] == root_name[i])
            callers = sorted({group(p) for p in parents[i] if prim[p] != prim[i]})
            print(f'{root_name[i]:45s} nodes={n} group={group(i)} callers={callers}')
