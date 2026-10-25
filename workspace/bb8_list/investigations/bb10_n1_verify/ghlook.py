from fw import *
w = '1' + '011' * 4 + '01' * (3 * 0 + 1) + '1010'
for x in stream(GH8, [('k', w, len(w), 'G')], 2000, 'G0r,G1r,H0r,H1r', 40):
    print(show(x)[:200])
