"""Stage 0 pieces: ST0a = K(0^(M+1); 1; 3b+1) -> W0 (explorer's stuck point); ST0b = W0 with the zero runs merged."""
import sys, time
from parts import *

def find_w0():
    s, t, pos = PARTS['ST0free']
    cfg = s
    while True:
        ops, cfg2, how = mexp.run_stuck(cfg, None)
        assert how == 'stuck', how
        lp = mexp.find_loop(cfg2, 2)
        if lp is None:
            return cfg2
        cfg = lp.after()

def merge_zeros(cfg):
    q, L, R, mode = cfg
    assert mode == '<' and L[0] == ('run', (1, 0, 1), (('M', 1),)), L[:2]
    blk = L[1]
    assert blk[0] == 'run' and blk[1] == (1, 0, 1) * 8 and blk[2] == (('b', 1),), blk
    return (q, [('run', (1, 0, 1), (('Z', 1),))] + L[2:], R, mode)

if __name__ == '__main__':
    t0 = time.time()
    W0 = find_w0()
    print('W0 =', pl.show(W0), '(%.1fs)' % (time.time() - t0))
    W1 = merge_zeros(W0)
    print('W1 =', pl.show(W1))
    ops, cfg2, how = mexp.run_stuck(W1, None)
    while how == 'stuck':
        print('  at', pl.show(cfg2))
        lp = mexp.find_loop(cfg2, 2)
        if lp is None:
            print('NO LOOP'); break
        ops, cfg2, how = mexp.run_stuck(lp.after(), None)
    print(how, pl.show(cfg2))

def cont(cfg, peels):
    peels = list(peels)
    while True:
        ops, cfg2, how = mexp.run_stuck(cfg, None)
        print('ops', ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops), how)
        print('  at', pl.show(cfg2)[-400:])
        if how != 'stuck':
            return cfg2
        lp = mexp.find_loop(cfg2, 2)
        if lp is not None:
            print('  loop on', lp.v_at); cfg = lp.after(); continue
        if not peels:
            print('NO LOOP'); return cfg2
        v, k = peels.pop(0)
        print('  PEEL', v, k)
        cfg = engine.subst(cfg2, v, ((v, 1),), k)
