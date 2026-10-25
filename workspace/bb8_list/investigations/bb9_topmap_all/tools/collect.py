import sys, os; BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, BASE); import idle
"""collect.py: gather every 9-state machine string (9 rows, '---' = halt/undefined) from the M8-extension sets listed in
SRCS (files or dirs, recursive over .tsv/.txt), dedupe, tag sources, mark the h003 family (bb9_topmap trees) as DONE.
Output: machines.tsv  (id  machine  sources  done_flag)."""
import re, glob, collections
INV = os.path.dirname(BASE)
SRCS = ['halt_redirect/c7/mf_out.tsv', 'bb9_redir/runs', 'bb9_c7triage/rank_all.tsv', 'bb9_c7triage/list_h.txt',
        'bb9_c7triage/list_s.txt', 'bb9_c7triage/list_t4.txt', 'bb8_resid/covers9_3e8.txt', 'bb8_resid/cov', 'bb8_resid/f1',
        'bb8_resid/f2r6', 'bb8_resid/r9', 'bb8_resid/list_f1.txt', 'bb8_resid/q5i', 'bb8_resid/q5i150', 'bb8_resid/f2',
        'bb9_y1_fable/f3_list.txt', 'bb9_y1_fable/f4_list.txt', 'bb9_y1_fable/runs']
RX = re.compile(r'(?<![0-9A-Z_-])((?:[01-][LR-][A-Z-]){2}(?:_(?:[01-][LR-][A-Z-]){2}){8})(?![0-9A-Z_-])')
def files(p):
    p = os.path.join(INV, p)
    if os.path.isfile(p): return [p]
    out = []
    for d, _, fs in os.walk(p):
        out += [os.path.join(d, f) for f in fs if f.endswith(('.tsv', '.txt'))]
    return out
src = collections.defaultdict(set)
for s in SRCS:
    tag = s.replace('/', ':')
    for f in files(s):
        if os.path.getsize(f) > 50e6: continue
        try:
            with open(f, errors='replace') as fh:
                for i, l in enumerate(fh):
                    if i > 200000: break
                    for m in RX.findall(l): src[m].add(tag)
        except Exception as e: print('skip', f, e)
done = set()
for tsv in glob.glob(os.path.join(INV, 'bb9_topmap', 'runs', 'A_*', 'tree.tsv')):
    for l in open(tsv):
        p = l.split('\t')
        if len(p) > 2: done.add(p[1])
M8E = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_'
with open(os.path.join(BASE, 'machines.tsv'), 'w') as fo:
    for i, m in enumerate(sorted(src)):
        fam = 'M8E' if m.startswith(M8E) and m[35:48] == '1RG1LD_0RG0RF' else ('M8pre' if m.startswith(M8E) else 'other')
        fo.write('m%05d\t%s\t%s\t%s\t%s\n' % (i, m, fam, 'DONE_h003fam' if m in done else '-', ','.join(sorted(src[m]))))
print(len(src), 'machines;', len(done & set(src)), 'in h003 family trees;', collections.Counter(
    ('M8E' if m.startswith(M8E) and m[35:48] == '1RG1LD_0RG0RF' else ('M8pre' if m.startswith(M8E) else 'other')) for m in src))
