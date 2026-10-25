import idle, glob, collections, os
files = glob.glob('**/*.tsv', recursive=True) + glob.glob('../../bb7_holdouts/**/*.tsv', recursive=True)
for f in sorted(files):
    g = f.replace(os.sep, '/')
    if '/out/c_' in g: continue
    try: L = open(f, errors='ignore').read().splitlines()
    except Exception: continue
    c = collections.Counter(); ns = collections.Counter()
    for l in L:
        x = l.split('\t')
        if len(x) > 4 and x[3] in ('LOOPER', 'REBUILD', 'W1-LOOPER', 'MULTI', 'MULTI?', 'W1-HALT?'):
            c[x[3]] += 1; ns[(len(x[0]) + 1) // 7] += 1
    if c: print(g, dict(c), dict(ns))
