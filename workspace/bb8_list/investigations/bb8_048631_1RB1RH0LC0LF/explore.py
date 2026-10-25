import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
TMS = "1RB1RH_0LC0LF_1LE1LD_0RE1LF_1RA1RD_0LG0LE_1LB1LF_1RF---"
pl.set_tm(TMS)
P = (0, 1)
l = [V('l')]
PH = {
 'T': (('E', mkrun(P, {'b': 1}) + [1, 0, 1] + l, [BLANK], '>'),
       ('E', mkrun(P, {'b': 1}, 3) + [1] + l, [BLANK], '>')),
 'R': (('E', mkrun(P, {'n': 1}, 1) + [1, 1] + l, [BLANK], '>'),
       ('E', mkrun(P, {}, 4) + [1] + mkrun(P, {'n': 1}) + l, [BLANK], '>')),
 'L1': (('E', mkrun(P, {'b': 1}) + [1, BLANK], [BLANK], '>'),
        ('E', mkrun(P, {'b': 1}, 3) + [BLANK], [BLANK], '>')),
 'RO': (('E', mkrun((0, 1, 0, 1), {'j': 1}) + [0, 1, BLANK], [BLANK], '>'),
        ('E', mkrun(P, {}, 2) + [1, 1] + mkrun((0, 1, 1, 1), {'j': 1}, 1) + [BLANK], [BLANK], '>')),
 'RE': (('E', mkrun((0, 1, 0, 1), {'j': 1}, 1) + [BLANK], [BLANK], '>'), None),
}
which = sys.argv[1:] or list(PH)
for nm in which:
    st, tg = PH[nm]
    try:
        script, cfg = drive(nm, st, tg, maxev=400, verbose=True)
    except pl.Halted as e:
        print('HALTED:', e)
print(sorted(pl.LEMMAS))
