import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
TM = "1RB1LE_0LC1RE_0RA0LD_1RA1LC_1LF0RC_1RG1LC_0LH1LG_1LB---"
pl.set_tm(TM)
ONE3 = (1, 1, 1); ONE6 = (1,)*6
R = [V('r')]
M = {'m': 1}; J = {'j': 1}
PH = {
 'R1': (('G', [BLANK], [0] + mkrun(ONE3, M) + [1, 1, 1, 0, 1] + R, '>'),
        ('G', [BLANK], [0] + mkrun(ONE3, M) + [1]*9 + R, '>')),
}
if __name__ == '__main__':
    for w in [a for a in sys.argv[1:] if a in PH]:
        s, t = PH[w]
        drive(w, s, t, matchers=(), maxev=200, verbose=True)
PH['R3'] = (('G', [BLANK], [0] + mkrun(ONE6, J) + [1]*5 + [0] + R, '>'),
            ('G', [BLANK], [0, 1, 1, 1] + mkrun((0,1,0,1,0,1), J) + [0, 1]*4 + [1] + R, '>'))
PH['Y5'] = (('G', [BLANK], [0] + mkrun(ONE6, J) + [1]*5 + [BLANK], '>'),
            ('G', [BLANK], [0, 1, 1, 1] + mkrun((0,1,0,1,0,1), J) + [0, 1]*4 + [1] + [BLANK], '>'))
PH['Y4'] = (('G', [BLANK], [0] + mkrun(ONE6, J) + [1]*4 + [BLANK], '>'),
            ('G', [BLANK], [0, 1, 1, 1] + mkrun((0,1,0,1,0,1), J) + [0, 1]*3 + [BLANK], '>'))
PH['Y3'] = (('G', [BLANK], [0] + mkrun(ONE6, J) + [1]*3 + [BLANK], '>'),
            ('G', [BLANK], [0] + [1]*11 + mkrun((0,1,0,1,0,1), J) + [0, 1] + [1, 1] + [BLANK], '>'))
PH['Y1'] = (('G', [BLANK], [0] + mkrun(ONE6, J) + [1]*1 + [BLANK], '>'),
            ('G', [BLANK], [0] + [1]*11 + mkrun((0,1,0,1,0,1), J) + [BLANK], '>'))
if __name__ == '__main__':
    for w in [a for a in sys.argv[1:] if a in PH and a != 'R1']:
        s, t = PH[w]
        drive(w, s, t, matchers=(), maxev=200, verbose=True)
