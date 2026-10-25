from tailvisit import T, runs
def visit_from(q, w, p, maxs=10**6):
    """head at index p of w (w = tail region, index 0 = first tail cell); run until head goes left of 0"""
    tape = [int(c) for c in w]
    for st in range(maxs):
        if p < 0: return ('exit', q, ''.join(map(str, tape)).rstrip('0'), st)
        while p >= len(tape): tape.append(0)
        t = T[(q, tape[p])]
        if t is None: return ('HALT', q, ''.join(map(str, tape)), st)
        tape[p] = t[0]; p += t[1]; q = t[2]
    return ('timeout', q, ''.join(map(str, tape)).rstrip('0'), maxs)
for j in range(0, 3):
    w = '1'*8 + '00111111'*j + '001001'
    res = visit_from('B', w, len(w))
    print('leftward pass j=%d:' % j, res[0], res[1], res[3], repr(res[2]), runs(res[2]))
    tw = res[2]
    for q in 'ABDEFGH':
        r2 = visit_from(q, tw, 0)
        print('   entry', q, r2[0], r2[1], r2[3], runs(r2[2]) if r2[0] != 'HALT' else r2[2])
