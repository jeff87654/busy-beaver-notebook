import idle, sys, subprocess, re
from tm import *
"""Extract the post-gadget structure: at the first K-like moment after H (state E, head on 0, left blank), parse
E>0 1 00 (11)^a 00 [(11)^d 00]* then MARKER then [(11)^d 00]* 1 0^inf (tail). Return (a, prefix digits, marker, tail digits)."""
def first_moment(M, a, n, maxs=10**8):
    T, _ = parse(M)
    r = Run(T, kword(a, [0] * n), 0, 4)
    hseen = False
    for _ in range(maxs):
        if not r.step(): return None
        if r.q == 7: hseen = True
        if hseen and r.q == 4 and r.tape[r.p] == 0 and not any(r.tape[:r.p]):
            nz = [i for i in range(len(r.tape) - 1, -1, -1) if r.tape[i]]
            return ''.join(str(v) for v in r.tape[r.p:nz[0] + 1]), r.steps
    return None
def split(w):
    assert w.startswith('0100')
    i = 4; a = 0
    while w[i:i + 2] == '11': a += 1; i += 2
    if w[i:i + 2] != '00': return None
    i += 2; pre = []
    while True:
        j = i; d = 0
        while w[j:j + 2] == '11': d += 1; j += 2
        if w[j:j + 2] == '00' and j + 2 <= len(w) - 1: pre.append(d); i = j + 2
        else: break
    # tail: longest suffix of form ((11)^d 00)* 1
    best = len(w) - 1; k = len(w) - 1  # w[k] = final '1'
    tail = []
    while True:
        j = k
        if w[j - 2:j] != '00': break
        j -= 2; d = 0
        while j >= 2 and w[j - 2:j] == '11': d += 1; j -= 2
        if j < i: break
        tail.insert(0, d); k = j
    return a, pre, w[i:k], tail
if __name__ == '__main__':
    for M in sys.argv[1:]:
        for a, n in [(21, 20), (24, 20), (21, 21), (30, 25)]:
            w, st = first_moment(M, a, n)
            a2, pre, mk, tail = split(w)
            # trim tail: the generic tail is all 1s; move non-1 leading tail digits into the marker
            print(M[14:20], M[-6:], (a, n), 'step', st, 'a=%d' % a2, 'pre(%d)=%s' % (len(pre), ','.join(map(str, pre[-6:]))), 'MARKER=%r' % mk,
                  'tail(%d)=%s' % (len(tail), ','.join(map(str, tail[:6]))))
