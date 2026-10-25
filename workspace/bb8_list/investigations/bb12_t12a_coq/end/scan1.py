import sys
sys.path.insert(0, '../ana')
from macro2 import *
from r2end import per_word
def outcome(k, p, K, n, a, nev=40):
    out = []
    R = Run({}, verbose=False, stop_after=lambda w, ev: False)
    wd = per_word(k, p, K, n, a)
    r = run_lit(wd, len(wd), 'H')
    seq = []
    while r[0] == 'B':
        word = r[1]
        while True:
            w2 = R.clr(word)
            if w2 is None: break
            word = w2
        far, tk = fmt_word(word)
        seq.append((len(far), comp(tk), r[2]))
        if len(seq) > nev: return seq, 'MANY'
        r = run_lit(word, len(word), 'H')
    return seq, r[:3]
if __name__ == '__main__':
    k, p, K, a = map(int, sys.argv[1:5])
    for n in range(int(sys.argv[5]), int(sys.argv[6])):
        seq, end = outcome(k, p, K, n, a)
        i = [j for j, s in enumerate(seq) if s[1].endswith('1^4 0 40')][0]
        print(n, n % 6, len(seq), end, '|', ' || '.join(s[1][-60:] for s in seq[i+1:]))
