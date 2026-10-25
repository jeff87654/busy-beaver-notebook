import sys, pickle
from common import *
from phases import *
import mexp
L0 = [0, 1, 1, 0, run((1, 1, 0) * 5, n=1), 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, BLANK]
R0 = [1, 1, 1, 0] + [1, 0] * 7 + [0, run(Z, J=1), 1, 0, 1, BLANK]
START = ('E', L0, R0, '<')
cfg, how = drive(START, verbose=False)
pickle.dump(cfg, open('st0_stuck1.pkl', 'wb'))
mexp.debug_loop(cfg, depth=2, width=600)
