from nextA import from_word, word_of
from lit import compress
for j in range(0, 4):
    for n in range(1, 40):
        w = '1' * n + ('001' + '1'*(j-1) if j else '')
        r, s = from_word(w)
        print(j, n, n % 6, r, s.steps, compress(word_of(s)) if r == 'A0' else s.show(), s.ones() if r=='HALT' else '')
    print()
