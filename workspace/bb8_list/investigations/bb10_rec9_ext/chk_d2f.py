import fext, follow3 as F
from numres import tau
REC = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---'
s = fext.d2_input()
st = F.Stage(REC, s, {'R1': tau(), 'R2': tau()}, {'R1': 2, 'R2': 3}, 200000000, print, True, start='B')
o = st.run_at({'R1': 210, 'R2': 212})
print(o['raw'][:200])
w = F.word_of(F.inst(s, {'R1': 210, 'R2': 212}))
print(len(w), w[-60:])
