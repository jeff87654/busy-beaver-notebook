import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\rank\f3')
import resA
# A1/A2 rules. E(A): A%4==0 H; 1 -> [3,2^3m,1;2]; 2 -> [3,2^(3m+1);2]; 3 -> [3,2^3m,1;14].
# E1 [0;a] == E(a+2) with one fewer 2; E2 [0,0;a] == E(a) with one more 2 (rules.py E_A1 extra)
def rebuild(A, extra, nrep):
    r = A % 4
    if r == 0: return None
    n0 = {1: 0, 2: 1, 3: 0}[r] + extra          # n mod 3 offset
    tail = [1] if r in (1, 3) else []
    a = 14 if r == 3 else 2
    n = nrep * 3 + (n0 % 3)
    return [3] + [2] * n + tail, a
def chain(variant, A, rounds=12, nrep=40):
    out = []
    for k in range(rounds):
        if variant == 'E': A2, extra = A, 0
        elif variant == 'E1': A2, extra = A + 2, -1
        else: A2, extra = A, +1
        out.append('%s(A%%4=%d)' % (variant, A2 % 4))
        rb = rebuild(A2, extra, nrep)
        if rb is None: out.append('HALT'); return out
        ds, a = rb
        variant, A = resA.run_list(ds, a)
    out.append('...'); return out
if __name__ == '__main__':
    v, A = sys.argv[1], int(sys.argv[2])
    for nrep in (40, 41, 57):
        print(nrep, ' -> '.join(chain(v, A, nrep=nrep)))
