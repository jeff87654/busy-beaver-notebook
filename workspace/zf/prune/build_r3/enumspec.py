"""Print a candidate's abstract enumerator in coq/Enum.v syntax: clause table (with parameter roles
resolved to p1/p2/p3) and axiomorder.  usage: python enumspec.py NAME.json > NAME.enum.v.txt"""
import sys, json, forms, zfp
cfg = json.load(open(sys.argv[1]))
cl = cfg['clauses']; perm = cfg.get('perm', {}); vm = cfg.get('vmap', {}); fl = cfg.get('flips', {})
SCHEMA = {
    'B1': '(wim (wim A B) (wim (wim B C) (wim A C)))', 'B2': '(wim (wim (wn A) A) A)',
    'B3': '(wim A (wim (wn A) B))', 'Y_CpCCNqCCqrNpq': '(wim A (wim (wim (wn B) (wim (wim B C) (wn A))) B))', 'B4': '(wim (wal A (wim B C)) (wim (wal A B) (wal A C)))',
    'B6b': '(wim (wal A (wal B C)) (wal B (wal A C)))', 'B6c': '(wim (wex A (wal A B)) B)',
    'B7': '(wex A (weq A B))', 'B8a': '(wim (weq A B) (wim (weq A C) (weq B C)))',
    'B8b': '(wim (weq A B) (wim (wel A C) (wel B C)))', 'B8c': '(wim (weq A B) (wim (wel C A) (wel C B)))',
    'B6a': '(wa (wim (weq A B) (wal C (weq A B))) (wim (wel A B) (wal C (wel A B))))   (* moot 0 if C = A or C = B *)',
    'DET': '(* pops minor ph then major maj; result A if maj = (wim ph A) else 0 *)',
    'GEN': '(* pops ph; result (wal A ph) *)',
    'B8bc': '(wim (weq A B) (wa (wim (wel A C) (wel B C)) (wim (wel C A) (wel C B))))',
}
def coq(t):
    k = t[0]
    if k == 'ph': return 'A'
    if k in ('eq', 'el'): return f'(w{k} c{t[1]} c{t[2]})'
    if k == 'n': return f'(wn {coq(t[1])})'
    if k in ('al', 'ex'): return f'(w{k} c{t[1]} {coq(t[2])})'
    if k == 'im': return f'(wim {coq(t[1])} {coq(t[2])})'
    if k == 'a': return f'(wa {coq(t[1])} {coq(t[2])})'
for i, c in enumerate(cl):
    p = perm.get(c, [1, 2, 3])
    if c in forms.TREES:
        body = coq(forms.variant(forms.TREES[c], tuple(vm.get(c, (0, 1, 2, 3))), fl.get(c, 0)))
    else:
        body = SCHEMA[c]
    for role, reg in zip('ABC', p):
        body = body.replace(role + ' ', f'p{reg} ').replace(role + ')', f'p{reg})')
    print(f'Definition clause_{i} (p1 p2 p3 : nat) : nat := {body}.   (* {c}; roles A,B,C = p{p[0]},p{p[1]},p{p[2]} *)')
print(f"Definition axiomorder : list nat := [{'; '.join(map(str, cfg['order']))}].")
print('(* positions: ' + ' '.join(cl[i] for i in cfg['order']) + ' *)')
print('(* program options: ' + ' '.join(cfg.get('opt', [])) + ' *)')
