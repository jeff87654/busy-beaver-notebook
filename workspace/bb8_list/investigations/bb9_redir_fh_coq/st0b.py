import pickle
from common import *
from planner8 import is_run
E0 = pickle.load(open('E0cfg.pkl', 'rb'))
q, L, R, mode = E0
rpos = [k for k, t in enumerate(L) if is_run(t) and t[2] == (('r', 1),)][0]
B12 = L[rpos][1]
L0 = L[:rpos] + list(B12) * 3 + [run(B12 * 5, w=1)] + L[rpos + 1:]
START = (q, L0, R, mode)
# target: Kf (1^(2n + i) 7 6 8 9^n) 1 0 with n = 4w + 4 (to be confirmed)
