"""br_batch.py IN OUT: backward-reasoning (sound) reachability of every undefined slot, per machine (depth 40)."""
import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen')
import idle  # noqa
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_topmap_all\tools')
import backref_s as br
done = set(l.split('\t')[0] for l in open(sys.argv[2])) if os.path.exists(sys.argv[2]) else set()
with open(sys.argv[2], 'a', newline='\n') as o:
    for m in open(sys.argv[1]).read().split():
        if m in done: continue
        res = br.check(m, 40)
        o.write('%s\t%s\n' % (m, res)); o.flush()
