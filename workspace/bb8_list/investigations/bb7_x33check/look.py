import idle, sys
from sim import *
m = X if sys.argv[1]=='X' else I
N = int(sys.argv[2]); state = sys.argv[3]
def show(n, tape, pos, st):
    if 'ABCDEFG'[st] == state and tape.get(pos,0)==0 and (pos < min(tape) or pos > max(tape) or True):
        # only print at tape edges
        if pos <= min(k for k in tape if tape[k]) - 1 or pos >= max(k for k in tape if tape[k]) + 1:
            s = rle(tape, pos, st)
            print(n, s.strip('0') if len(s) < 400 else s[:400])
r = run(m, N, show)
print(r[:5])
