import pickle, sys
from macro2 import *
ev = pickle.load(open('ev_17_36.pkl','rb'))
FAR192,_ = fmt_word(ev[139]['inp'])
def mkw(m, A, far=FAR192, left=(2,2,0)):
    return far + ''.join(D(x) for x in list(left) + [33,2,0] + [3,2,0]*(m-1) + [1]*4) + D(0) + D(A)
if __name__ == '__main__':
    for A in (10, 40):
        for m in range(1, 40):
            w = mkw(m, A)
            r = run_lit(w, len(w), 'H', maxsteps=10**8)
            if r[0] == 'B':
                far, tk = fmt_word(r[1])
                print(A, m, m % 6, r[2], len(far), comp(tk))
            else: print(A, m, r[:3])
