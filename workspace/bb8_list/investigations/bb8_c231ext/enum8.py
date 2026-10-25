import idle
"""Enumerate 8-state halt-redirect extensions of champ_231/232: C1 -> wdH, H = one halt + one (w,d,X), X in A..H."""
from tm import C231, C232
def ext(base):
    rows = base.split('_'); out = []
    for cw in '01':
        for cd in 'LR':
            r = rows[:]; r[2] = r[2][:3] + cw + cd + 'H'
            for hs in (0, 1):
                for w in '01':
                    for d in 'LR':
                        for X in 'ABCDEFGH':
                            h = ['---', '---']; h[1 - hs] = w + d + X
                            out.append('_'.join(r + [''.join(h)]))
    return out
if __name__ == '__main__':
    ms = [(m, 'c231') for m in ext(C231)] + [(m, 'c232') for m in ext(C232)]
    with open('ext8.txt', 'w', newline='\n') as f:
        for m, b in ms: f.write(m + '\t' + b + '\n')
    print(len(ms))
