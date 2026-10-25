"""ex.py SPEC : expand '(a b c)xN' groups and bare tokens to ms 'i' tokens (tok^n). Output 'X:...' for dz.py/grp.py."""
import re,sys
s=sys.argv[1]
head,body=s.split('|',1)
def exp(b):
    while '(' in b:
        b=re.sub(r'\(([^()]*)\)x(\d+)',lambda m:' '.join([m.group(1)]*int(m.group(2))),b)
    out=[]
    for t in b.split():
        if t.startswith('['): out.append(t); continue
        out.append(t if '^' in t else t+'^1')
    return ' '.join(out)
print('X:'+head.strip()+' | '+exp(body))
