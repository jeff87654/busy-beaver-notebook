from rlib import *
w = word('2 5 1^79 0^3 3 1^32 1 19')
r = twin(L12, w, 6, '1')
print(r['raw']); print(r['base'].get('desc'), r['bmax'], r['read'], '//', r['div']); print(r['pat'])
