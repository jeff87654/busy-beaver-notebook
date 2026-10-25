from nextA import from_word, word_of
from lit import compress
for n in range(1, 25):
    w = '1' * n + '011'*3 + '0011'
    r, s = from_word(w)
    print('R2', n, n % 6, r, s.steps, compress(word_of(s)) if r == 'A0' else s.show())
for n in range(1, 25):
    for m in (1,2,3):
        w = '1' * n + '0'*m + '11111' + '011'*2 + '0011'
        r, s = from_word(w)
        print('R1', n, m, n % 4, r, s.steps, compress(word_of(s)) if r == 'A0' else s.show())
