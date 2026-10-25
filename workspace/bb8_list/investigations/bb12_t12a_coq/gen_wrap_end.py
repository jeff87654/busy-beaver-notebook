"""B-form wrappers of the round-2-end event lemmas (draft statements; see gen_wrap.py)."""
import sys
import gen_wrap as GW
from evs_end import *
GW.EV = EVE
if __name__ == '__main__':
    for n in sys.argv[1:]:
        try:
            w = GW.wrapper(n)
            if n == 'F23':
                w = w.replace('bnorm. ', 'bnorm. rewrite (tok9 43 y). ')
            if n == 'G1':
                w = w.replace('rewrite (pow_mul [1;0;1]%sym 2 a).', 'rewrite (pow_add [1;0;1]%sym 6 (2 * a)), (pow_mul [1;0;1]%sym 2 a).')
            print(w)
        except Exception as e:
            print('(* %s: %s *)' % (n, e))
