"""bform.py: build cfollow start lines from n1-style B-forms [L1,..,Ln | A] = D(L1)..D(Ln) D0 D(A) _H>  (D(x) = (10)^x 1),
head on the blank right of the last 1, state index QH (default 7 = H).
usage: python bform.py "2,1*90,0,1*35|6" [...]   ;  --check MACHINE STEPS FORM  (literal run from blank, compare)"""
import sys
def cells(form):
    L, A = form.split('|'); toks = []
    for it in L.split(','):
        if '*' in it: v, k = it.split('*'); toks += [int(v)] * int(k)
        elif it: toks.append(int(it))
    w = ''
    for x in toks + [0, int(A)]: w += '10' * x + '1'
    return w
def rle(w):
    out = [w[0]]; run = 0; cur = w[0]
    for ch in w:
        if ch == cur: run += 1
        else: out.append(str(run)); cur = ch; run = 1
    out.append(str(run)); return ' '.join(out)
if sys.argv[1] == '--check':
    m, N, form = sys.argv[2], int(sys.argv[3]), sys.argv[4]
    rows = m.split('_'); T = {}; pos = 0; q = 0
    for st in range(N):
        c = T.get(pos, 0); t = rows[q][3*c:3*c+3]
        T[pos] = int(t[0]); pos += 1 if t[1] == 'R' else -1; q = ord(t[2]) - 65
    lo = min(k for k in T if T[k]); hi = max(k for k in T if T[k])
    tape = ''.join(str(T.get(k, 0)) for k in range(lo, hi + 1))
    print('state', chr(65+q), 'head-hi', pos - hi, 'match', tape == cells(form))
else:
    qh = 7
    args = sys.argv[1:]
    if args and args[0] == '--file': args = [l.strip() for l in open(args[1]) if l.strip()]
    for f in args:
        w = cells(f); print(qh, len(w), rle(w))
