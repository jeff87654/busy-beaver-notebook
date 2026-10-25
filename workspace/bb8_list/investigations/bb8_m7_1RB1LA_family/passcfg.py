import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w_fam import *
def pass_rule():
    return (PS(3, {'z': 1}, 2, {'c': 1}, 0, {'d': 1}), PS(2, {'z': 1}, 1, {'c': 1}, 1, {'d': 1}))

def passb_rule():
    return (PSB(2, {'c': 1}, 0, {'d': 1}), PSB(1, {'c': 1}, 1, {'d': 1}))
