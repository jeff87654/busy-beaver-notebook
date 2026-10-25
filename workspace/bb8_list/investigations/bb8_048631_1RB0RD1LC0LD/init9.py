import sys, pickle, time
import planner9 as P
import fam9 as F
from planner9 import C
start = ('A', [P.BLANK], [P.BLANK], '>')
target = F.PA(C(216), C(214), C(143))
t = time.time()
script, got = P.drive_until_string2('INIT', start, target, matchers=[F.m_TL], maxev=200000, maxlit=3000000)
print('time %.1f' % (time.time() - t))
if script:
    print('ops', len(script), 'lit', sum(len(o[1]) for o in script if o[0] == 'lits'), 'TL uses', sum(1 for o in script if o[0] == 'coq' and 'TLs' in o[1]),
          'cross', sum(1 for o in script if o[0] == 'coq' and o[1].startswith('follow cr')))
    print(P.show(got)[:300])
    pickle.dump((start, script, got), open('init9.pkl', 'wb'))
else:
    print('no match', P.show(got)[:300])
