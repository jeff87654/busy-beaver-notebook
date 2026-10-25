import sys
from gen_base import table
TM = "1RB0RC_1LA1RF_0RE0LD_1LE0LH_1LA0LG_1RA0LF_0LC1LE_---1LF"
subst = dict(tm=TM, table=table(TM))
out = open('head.v.in').read() % subst
for f in sys.argv[2:]:
    out += open(f).read() + '\n'
open(sys.argv[1], 'w', newline='\n').write(out)
