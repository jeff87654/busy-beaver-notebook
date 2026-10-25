import idle, sys
from tm import TM
# slotev.py MACHINE N SLOT[,SLOT..] : print the tape view each time one of the slots is read (first 40 times)
m = sys.argv[1]; N = int(sys.argv[2]); S = sys.argv[3].split(','); mx = int(sys.argv[4]) if len(sys.argv) > 4 else 40
M = TM(m); k = 0
while M.steps < N:
    s = chr(65 + M.q) + str(M.t.get(M.pos, 0))
    if s in S:
        print(M.steps, s, M.view(500)); k += 1
        if k >= mx: break
    if not M.step(): print('HALT', M.steps, M.halted); break
