from w891 import *
import passcfg, itertools
G = lambda **kw: [dict(zip(kw, v)) for v in itertools.product(*kw.values())]
s, t = passcfg.pass_rule()
print('Pass', chk(s, t, G(z=range(3), c=range(4), d=range(3))))
