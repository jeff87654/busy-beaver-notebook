import sys
sys.path.insert(0, '../ana')
from bsim import *
from view import view
# B-form after CLR: far | 2 2 0 X 2 0 (3 2 0)^n 1^4 0 A
def eat_word(n, X=33, A=40, far=None):
    far = far if far is not None else (D(2)*8 + D(1) + D(8) + '00' + D(3) + D(10) + D(2)*17 + '111' + '00' + '1' + '00000' + '1' + '00000' + '1' + '00000')
    return far + D(2) + D(2) + D(0) + D(X) + D(2) + D(0) + (D(3)+D(2)+D(0))*n + D(1)*4 + D(0) + D(A)
n = int(sys.argv[1])
w = eat_word(n)
PAD = 1 << 12
t = bytearray(PAD) + bytearray(int(c) for c in w) + bytearray(PAD)
h = len(w) + PAD; q = 'H'; steps = 0
base = PAD
lo = h; snaps = []
while True:
    tr = TT[(q, t[h])]
    if tr is None: print('halt'); break
    wv, d, q = tr; t[h] = wv; h += d; steps += 1
    if q == 'H' and t[h] == 0 and t.find(1, h) < 0 and steps > 10:
        print('B-form at', steps); break
    if h < lo:
        lo = h
        if (len(w) + PAD - lo) % 9 == 0: snaps.append((steps, len(w)+PAD-lo))
print(snaps[:60])
a = t.find(1); b = t.rfind(1)
print(view(''.join(map(str, t[a:b+1]))))
