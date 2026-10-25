from lib import *
# (1) start-up from blank: B-form events
snaps, end = run(M10, '', 'A', '', 200000, ['snap=G0', 'bform', 'maxsnap=100'])
for s in snaps[:60]:
    t = tokens(s[1])
    print(s[0], ctok(t))
