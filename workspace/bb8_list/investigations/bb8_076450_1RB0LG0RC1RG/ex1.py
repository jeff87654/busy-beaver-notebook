from planner8 import *
abb = bits('abb'); bab = bits('bab')
N = {'n': 1}
start = ('A', [BLANK], [0] + mkrun(abb, N, 1) + list(bab) + [V('r')], '>')
script, cfg = drive('R_P explore', start, None, maxev=60)
