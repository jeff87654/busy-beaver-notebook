import sys
sys.path.insert(0, '../ana')
from macro2 import *
from view import view
from r2end import per_word
k, p, K, n, a = map(int, sys.argv[1:6])
R = Run({}, verbose=False)
wd = per_word(k, p, K, n, a)
print('START', view(wd))
r = run_lit(wd, len(wd), 'H')
while r[0] == 'B':
    word = r[1]; st = r[2]
    while True:
        w2 = R.clr(word)
        if w2 is None: break
        print('   CLR'); word = w2
    print(st, view(word))
    r = run_lit(word, len(word), 'H')
print(r[:3], view(r[3]) if r[0]=='HALT' else '')
