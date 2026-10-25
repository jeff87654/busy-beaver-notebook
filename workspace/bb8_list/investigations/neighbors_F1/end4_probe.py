import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\neighbors_family_tools')
from tmlit import Sim, ST
from kfam import parse_at
for tm in sys.argv[1:]:
    print(tm)
    for i in range(0, 7):
        w = '11' + '0' + '10' * i
        s = Sim.from_word(tm, '0000' + w + '0000', 4 + 2, 'C')
        while s.steps < 100000:
            if not s.step():
                print('  i=%d HALT' % i); break
            if parse_at(s) is not None:
                lo, hi = s.bounds()
                print('  i=%d steps %d: %s B>   %s' % (i, s.steps, ''.join(map(str, s.tape[lo:s.pos])), parse_at(s)))
                break
