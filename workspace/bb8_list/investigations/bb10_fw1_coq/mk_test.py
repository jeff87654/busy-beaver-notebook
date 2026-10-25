"""Write a standalone test .v with the header, all crossing lemmas, and the lemmas of the given parts (from gen_cache).
  python mk_test.py OUT.v PART,PART"""
import sys, pickle
from parts import *
import coqgen_util
out, names = sys.argv[1], sys.argv[2].split(',')
lemmas, crosses = [], {}
for name in names:
    (lems, st), cr = pickle.load(open(HERE / 'gen_cache' / ('%s.pkl' % name), 'rb'))
    lemmas.extend(lems); crosses.update(cr)
cl = ''.join(coqgen_util.crossing_lemma(nm, crosses[nm]) + '\n' for nm in sorted(crosses))
open(out, 'w', newline='\n').write(header('test') + '\n' + cl + '\n' + '\n'.join(lemmas))
