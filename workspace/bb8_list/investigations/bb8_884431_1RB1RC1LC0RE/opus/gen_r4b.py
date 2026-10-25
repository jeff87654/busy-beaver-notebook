import sys, time
from common import *
from rules_r4 import M, G
t0 = time.time()
lem, rule = gen_rule('R4b', M, G, False)
print('generated in %.1fs' % (time.time() - t0), file=sys.stderr)
text = header('test R4b') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lem) + '\n' + rule
open(sys.argv[1], 'w', newline='\n').write(text)
