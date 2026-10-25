"""Quick Coq check that the final reached configuration of each exploration equals its target (finish_norm)."""
import sys
from pathlib import Path
from common import *
import mexp, gen_rebuild, gen_d2, gen_rules


def ends(node, acc):
    for it in node['items']:
        if it[0] == 'split':
            for b in (it[3], it[4]):
                if b is not None:
                    ends(b, acc)
    if 'end' in node and not node.get('halt'):
        acc.append((node['end'], node['target']))
    return acc


items = [(n, s, t, p) for n, s, t, p in gen_rules.ITEMS] + [('RB', gen_rebuild.START, gen_rebuild.TARGET, ()),
                                                          ('D2', gen_d2.START, gen_d2.TARGET, ())]
out = []
k = 0
for name, s, t, pos in items:
    tree = mexp.explore(s, t, positive=frozenset(pos))
    for a, b in ends(tree, []):
        k += 1
        cn, vs = coqgen.free_vars(a, b)
        out.append('Lemma END_%s_%d : forall %s, %s -->* %s.\nProof. intros. finish_norm. Qed.\n'
                   % (name, k, ' '.join(cn + vs), coqgen.cfg_coq(a), coqgen.cfg_coq(b)))
Path('T_end.v').write_text(header('end check') + '\n' + '\n'.join(out), newline='\n')
print(k, 'end checks')
