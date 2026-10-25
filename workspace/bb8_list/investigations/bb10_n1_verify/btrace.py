"""print B-form configurations of a run, suppressing standard R1/R2 transitions; specials are shown in full.
   btrace.py START MAXSTEPS MAXEV [all]   START = 'B:t1,t2,..:A' (t may be x^k) or 'K:n:b' (record template) """
import sys
from fw import *


def parse_list(s):
    out = []
    for x in s.split(','):
        if not x:
            continue
        if '^' in x:
            v, k = x.split('^'); out += [int(v)] * int(k)
        else:
            out.append(int(x))
    return out


def classify(P, C):
    """P, C: (list, A). return 'R1', 'R2', or None."""
    L, A = P; M, A2 = C
    if L and L[-1] >= 3 and M == L[:-1] + [L[-1] - 3] and A2 == 2 * A + 8:
        return 'R1'
    if L and L[-1] == 1 and A2 == 4 and len(M) == len(L):
        j = len(L) - 1
        while j >= 0 and L[j] == 1:
            j -= 1
        if j >= 0 and L[j] >= 3:
            exp = L[:j] + [L[j] - 3, A + 3] + L[j + 2:]
            if M == exp:
                return 'R2'
    return None


if __name__ == '__main__':
    st = sys.argv[1]
    if st.startswith('B:'):
        _, ts, A = st.split(':'); w, h, q = bword(parse_list(ts), int(A))
    else:
        _, n, b = st.split(':'); w, h, q = K(int(n), int(b))
    showall = len(sys.argv) > 4
    prev = None
    cnt = {'R1': 0, 'R2': 0}
    for x in stream(M10, [('s', w, h, q)], int(float(sys.argv[2])), 'G0r,E0,J0', int(sys.argv[3])):
        if x['kind'] == 'EV' and x['q'] == 'G':
            p = bparse(x['word'], x['rel'])
            if p is None:
                continue
            c = classify(prev, p) if prev else None
            prev = p
            if c and not showall:
                cnt[c] += 1
                continue
            print('%d B [%s | %d]%s   (R1 x%d, R2 x%d since last)' % (x['step'], fmt(p[0]), p[1], ' '+c if c else '', cnt['R1'], cnt['R2']), flush=True)
            cnt = {'R1': 0, 'R2': 0}
        else:
            print(show(x)[:300], flush=True)
