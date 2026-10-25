import pickle, sys
from st0 import *
W0 = pickle.load(open('W0.pkl', 'rb'))
pre = int(sys.argv[1])
q, L, R, mode = merge_zeros(W0)
cfg = (q, [1, 0, 1] * pre + L, R, mode)
T = K([zeros(Z=1), tok(1) * (15 + pre), tok(5), tok(0), tok(2), tok(2), [run(tuple(tok(6)) * 4, b=1)], tok(6) * 2, [BLANK]], tok(1), tok(1))
for i in range(int(sys.argv[2])):
    ops, cfg2, how = mexp.run_stuck(cfg, T)
    s = pl.show(cfg2)
    print(i, how, 'ops', ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops)[:200])
    print('   ', s[-260:])
    if how != 'stuck': break
    lp = mexp.find_loop(cfg2, 2)
    if lp is None:
        print('NO LOOP'); break
    print('    loop on', lp.v_at)
    cfg = lp.after()
