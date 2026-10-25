"""Halt-redirect extensions of the records and their literal start tapes.

  python gen.py machines FAMILY > list.txt       FAMILY = c35 (E0 -> I, 9 states) | bb9 (I1 -> J, 10 states)
  python gen.py starts c35 BASE NLIST BLIST > starts.txt   K(0^n; 0; b) from the base's dlscan2 template
  python gen.py starts bb9 STATE BLIST R1LIST > starts.txt  the BB(9) record's halting-stage tape (follow2 stage 1)
Each extension defines the halt slot as xyN (N = the new state) and gives the new state one defined transition
and one halt, or two halts (both new transitions undefined).  A machine needs exactly one undefined transition
to halt, so at most one of the two new transitions is defined."""
import re
import sys

C35 = {
    'c35': ('1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF', 'R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=10101'),
    'c35gh': ('1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_0RG1LD_1RH1LG_1LC0RG', 'R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=1010'),
    'c35fh': ('1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC1RH_0LH0RF', 'R,F,P=1,u=01,s=1,d=3d+1,b=3b+0,S=10101010'),
    'c35h': ('1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LH', 'R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=10101'),
}
BB9 = {
    'rec9': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---',
    'rec9t': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RH0RE_0LH---',
}


def trans(nst):
    return [f'{w}{d}{chr(65 + q)}' for q in range(nst) for w in '01' for d in 'LR']


def extensions(base, slot_row, slot_sym, nst):
    rows = base.split('_') + ['------'] * (nst - len(base.split('_')))
    new = chr(65 + nst - 1)
    out = []
    for e in (f'{w}{d}{new}' for w in '01' for d in 'LR'):
        r = list(rows)
        cell = [r[slot_row][:3], r[slot_row][3:]]
        assert cell[slot_sym] == '---', (base, slot_row, slot_sym)
        cell[slot_sym] = e
        r[slot_row] = ''.join(cell)
        news = [('---', '---')] + [(t, '---') for t in trans(nst)] + [('---', t) for t in trans(nst)]
        for a, b in news:
            rr = list(r)
            rr[nst - 1] = a + b
            out.append('_'.join(rr))
    return out


def tmpl(t):
    g = re.match(r'([LR]),([A-P]),P=([01-]*),u=([01]+),s=([01]+),d=(\d+)d\+(\d+),b=(\d+)b\+(\d+),S=([01-]*)$', t)
    o, q, P, u, s, al, be, alB, beB, S = g.groups()
    return q, ('' if P == '-' else P), u, s, int(be), int(alB), int(beB), ('' if S == '-' else S)


def D(m):
    return '10' * m + '1'


def main():
    a = sys.argv[1:]
    if a[0] == 'machines':
        if a[1] == 'c35':
            for lab, (m, _) in C35.items():
                for x in extensions(m, 4, 0, 9):
                    print(f'{x}\t{lab}')
        elif a[1] == 'bb9':
            for lab, m in BB9.items():
                for x in extensions(m, 8, 1, 10):
                    print(f'{x}\t{lab}')
    elif a[0] == 'starts' and a[1] == 'c35':
        q, P, u, s, be, alB, beB, S = tmpl(C35[a[2]][1])
        for n in map(int, a[3].split(',')):
            for b in map(int, a[4].split(',')):
                w = P + (u * be + s) * (n + 1) + u * (alB * b + beB) + S
                print(f'n{n}b{b} {w} {len(w)} {q}')
    elif a[0] == 'starts' and a[1] == 'bb9':
        q = a[2]
        for b in map(int, a[3].split(',')):
            for r1 in map(int, a[4].split(',')):
                w = (D(0) * 2 + D(4) + D(21) + D(4) + D(2) + D(1) * (12 * b - 11) + D(1) + D(r1) + D(0) * 6
                     + ('100' + D(0) * 5) * 5 + '100' + '100' + D(0))
                print(f'b{b}r{r1} {w} {len(w)} {q}')


if __name__ == '__main__':
    main()
