"""Macro states of 884431 (from the Sonnet investigation: rules_r4.py, guess3.py), as engine configurations."""
from common import *
from rules884 import rules, U, U2, E
import rules_r4
RL = dict((n, (s, t)) for n, s, t in rules())
TT = [1, 1, V('t')]
start4, tgt4 = RL['R4m']
start3, tgt3 = RL['R3m']
M = rules_r4.M
G = rules_r4.G
PS, PT = rules_r4.PS, rules_r4.PT
M3 = ('E', [('run', (1, 0, 1, 0), (('b', 1),)), BLANK],
      [('run', (1, 1), (('k', 1),))] + [1] * 5 + [0, 1] * 4 + [1, 1] + mkrun(U, {'y': 1}) + TT, '<')
G3 = ('A', [BLANK], pl.norm_side(mkrun((1, 1), {'k': 1}, 0) + [1] * 6 + mkrun(U2, {'b': 1}) + [0, 1] * 3 + [1, 1]
                                + mkrun(U, {'y': 1}) + TT), '<')
