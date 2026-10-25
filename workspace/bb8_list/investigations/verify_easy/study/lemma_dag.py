"""Static profile of the generated files: per file, number of lemmas, total symbolic steps (sum of 'do N step' + single
'step'), intra-file lemma references, and the longest chain of intra-file dependencies (in steps).
   python -I lemma_dag.py DIR_WITH_dev_k31 [files...]"""
import re, sys, os, json
root = sys.argv[1]
files = sys.argv[2:]
LEM = re.compile(r'^(Lemma|Theorem|Corollary)\s+([A-Za-z0-9_\']+)', re.M)
out = {}
for f in files:
    src = open(os.path.join(root, f), encoding='utf-8').read()
    ms = list(LEM.finditer(src))
    names = [m.group(2) for m in ms]
    nameset = set(names)
    blocks = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(src)
        blocks.append((m.group(2), src[m.start():end]))
    steps = {}; deps = {}
    for n, b in blocks:
        proof = b[b.find('Proof.'):] if 'Proof.' in b else b
        s = sum(int(x) for x in re.findall(r'do (\d+) step', proof))
        s += len(re.findall(r'(?<![\w ]do \d)(?<!do \d\d)(?<!do \d\d\d)\bstep\b(?! *\.)', proof)) * 0
        steps[n] = s + len(re.findall(r'\bexecute\b', proof)) * 1
        ids = set(re.findall(r'[A-Za-z_][A-Za-z0-9_\']*', proof))
        deps[n] = sorted((ids & nameset) - {n})
    # longest chain (weighted by steps, +1 per lemma)
    memo = {}
    def chain(n):
        if n in memo: return memo[n]
        memo[n] = (steps[n] + 1) + max((chain(d) for d in deps[n]), default=0)
        return memo[n]
    tot = sum(steps[n] + 1 for n in names)
    crit = max((chain(n) for n in names), default=0)
    ndep = sum(1 for n in names if deps[n])
    roots = [n for n in names if not any(n in deps[m] for m in names)]
    out[f] = dict(lemmas=len(names), steps=tot, crit=crit, with_deps=ndep, roots=len(roots), bytes=len(src))
    print('%-22s %5d lemmas %8d steps  crit-chain %7d (%.0f%%)  lemmas-with-intra-deps %4d  top-level %4d  %8d B' % (
        f, len(names), tot, crit, 100.0 * crit / max(tot, 1), ndep, len(roots), len(src)))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lemma_dag.json'), 'w'), indent=1)
