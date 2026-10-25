import pickle, sys, time
from common import *
from phases import drive_peel
from st2 import S2
t0 = time.time()
cfg, how, peels = drive_peel(S2, {'r'}, verbose=False)
print(how, peels, '%.1fs' % (time.time() - t0)); print(pl.show(cfg)[:900])
pickle.dump((cfg, peels), open('st2_stuck.pkl', 'wb'))
