import sys
from nextA import from_word, word_of
from lit import compress
# U(n,m) = A0 1^n 0 1^m
bad = 0
for n in range(1, 80):
    for m in range(0, 12):
        w = '1'*n + ('0' + '1'*m if m else '')
        r, s = from_word(w, maxsteps=10**6)
        out = compress(word_of(s)) if r == 'A0' else s.show()
        if n % 6 != 5 or m == 0:
            if m <= 2: print('U', n, m, r, s.steps, out)
        else:
            j = (n-5)//6
            exp = '1'*(12*j+17) + ('0'+'1'*(m-1) if m > 1 else '')
            ok = r == 'A0' and word_of(s) == exp
            if not ok:
                bad += 1; print('MISMATCH', n, m, r, out)
print('bad', bad)
