"""Machine-level pieces of R4: R4a (start -> M), R4b (M -> G), PASS (G(j+2) -> G(j+1))."""
from rules884 import *

M = ('A', [('run', (1, 0, 1, 0), (('b', 1),)), BLANK], [('run', (1, 1), (('n', 1),))] + [1, 1, 1, 1, 0] + [1] * 8 + [BLANK], '<')
G = ('A', [BLANK], pl.norm_side(mkrun((1, 1), {'n': 1}, 2) + [0] + mkrun((1, 1, 1, 1), {'b': 1}, 2) + [BLANK]), '<')
start4 = cfg(kc(({'b': 1}, 0), [], mkrun(E, {'n': 1}, 0) + [1, 1, 1, BLANK]))
TP = [0, 1, V('w')]
PS = ('A', [BLANK], pl.norm_side([0] + mkrun((1, 1), {'j': 1}, 2) + TP), '>')
PT = ('A', [BLANK], pl.norm_side([0] + mkrun((1, 1), {'j': 1}, 1) + [0, 1, 1, 1] + TP), '>')

def pieces():
    return [('R4a', start4, M, True), ('R4b', M, G, False), ('PASSm', PS, PT, True)]
