"""All halting extensions of a 9-state base through I1 -> J: I1 in {0,1}x{L,R}xJ, one J slot undefined (the halt),
the other J slot any of the 40 transitions.  Usage: python gen_ext.py BASE > file"""
import sys
BASE = sys.argv[1] if len(sys.argv) > 1 else '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---'
rows = BASE.split('_')
assert rows[8].endswith('---')
ALL = [f'{w}{d}{s}' for w in '01' for d in 'LR' for s in 'ABCDEFGHIJ']
for i1 in ['0LJ', '0RJ', '1LJ', '1RJ']:
    r = rows[:8] + [rows[8][:3] + i1]
    for other in ALL:
        print('_'.join(r + [other + '---']))
        print('_'.join(r + ['---' + other]))
