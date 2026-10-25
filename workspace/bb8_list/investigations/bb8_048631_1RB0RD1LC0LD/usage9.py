"""Which transitions are used by the rules (planner replays), and by the initial segment."""
import pickle
import planner9 as P
import fam9 as F
used = {}
orig_step = P.step
def step(cfg):
    q, L, R, mode = cfg
    s = P.head(cfg)
    used.setdefault(CUR[0], set()).add((q, s))
    return orig_step(cfg)
P.step = step
orig_dc = P.derive_crossing
def derive_crossing(q, direction, xs, behind):
    # replay the crossing literally to record transitions
    nb = len(behind)
    if direction == '>':
        tape = list(reversed(behind)) + list(xs); pos = nb; exit_pos = nb + len(xs)
    else:
        tape = list(reversed(xs)) + list(behind); pos = len(xs) - 1; exit_pos = -1
    st = q
    for _ in range(5000):
        if pos == exit_pos or not (0 <= pos < len(tape)): break
        tr = P.T[(st, tape[pos])]
        used.setdefault(CUR[0], set()).add((st, tape[pos]))
        if tr is None: break
        w, d, st = tr; tape[pos] = w; pos += d
    return orig_dc(q, direction, xs, behind)
P.derive_crossing = derive_crossing
CUR = ['?']
import rounds
from planner9 import C
SC = pickle.load(open('rounds.pkl', 'rb'))
EN = pickle.load(open('endings.pkl', 'rb'))
for ph in 'ABC':
    CUR[0] = 'R' + ph
    tpl = SC[ph][0]
    rounds.run_round(ph, tpl)
import endings  # re-runs endings and init with recording under CUR '?'
