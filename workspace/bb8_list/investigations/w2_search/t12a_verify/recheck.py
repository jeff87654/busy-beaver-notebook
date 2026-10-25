"""recheck.py M PREFIX: re-run every dumped stage literally with lsim and compare with the follower's K-moment."""
import lsimpy, sys, os
M, pre = sys.argv[1], sys.argv[2]
s = 0; bad = 0; newreads = []
while os.path.exists(f'{pre}_{s}.txt'):
    w = open(f'{pre}_{s}.txt').read().strip()
    if os.path.exists(f'{pre}_{s}.k'):
        k = open(f'{pre}_{s}.k').read().split('\n'); tgt = [int(x) for x in k[0].split()]
        r = lsimpy.run(M, w, kmode=-1, target=tgt[::-1], maxs=10**11)
        ok = r['res'] == 'K' and r['far'] == k[1] and r['toks'] == tgt
        if not ok: bad += 1; print('MISMATCH at', s, r['line'][:100])
        cnt = r['line'][r['line'].index('cnt') + 4:r['line'].index('kmom')].split()
        nz = [c for c in cnt if not c.endswith(':0') and not c.startswith('J1')]
        if nz: newreads.append((s, ' '.join(nz)))
    else:
        r = lsimpy.run(M, w, kmode=0, maxs=10**11); print('final stage', s, r['line'][:70])
    s += 1
print('stages', s, 'mismatches', bad); print('new-state reads:', newreads)
