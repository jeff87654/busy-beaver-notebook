import sys
sys.path.insert(0,'.')
from coqgen_util import table
import phases884 as P
parts=sys.argv[2:]
head=open('head884.v.in').read().replace('@TABLE@',table(P.TM)).replace('@TM@',P.TM)
ph=open('phases_out.v').read()
tail=''.join(open(p).read() for p in parts)
open(sys.argv[1],'w',newline='\n').write(head+ph+tail)
