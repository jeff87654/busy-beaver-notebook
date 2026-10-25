import idle, sys
from tm import TM
# snap.py MACHINE t1 t2 ... : print full run-length tape at those steps
m = sys.argv[1]; ts = sorted(int(x) for x in sys.argv[2:])
M = TM(m)
for t in ts:
    while M.steps < t:
        if not M.step(): print('HALT', M.steps, M.halted); sys.exit()
    print(t, chr(65+M.q), M.view(3000))
