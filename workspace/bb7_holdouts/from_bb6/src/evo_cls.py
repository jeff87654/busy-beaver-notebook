"""evo_cls.py EVO.txt: label each machine from its evo snapshots.
ENGINE? = block count stable over the last half (max/min <= 1.5, >= 3 blocks), largest block grows >= 5x over the run,
          and the largest block is NOT monotone (some snapshot's largest < previous largest/1.5: transfers / resets).
GROWLIST = block count grows >= 2x over the last half. SMALL = final span < 1000. else OTHER."""
import sys
for l in open(sys.argv[1]):
    f = l.split(); m = f[0]; sn = []
    for x in f[1:]:
        if x in ('HALT', 'OOB'): sn.append(x); continue
        t, sp, nb, ex = x.split(':'); ex = [int(e) for e in ex.split('/')] if ex else [0]
        sn.append((int(t), int(sp), int(nb), ex))
    S = [s for s in sn if isinstance(s, tuple)]
    if not S: print(m, 'NONE'); continue
    if 'OOB' in sn: lab = 'OOB'
    elif 'HALT' in sn: lab = 'HALT'
    elif S[-1][1] < 1000: lab = 'SMALL'
    else:
        h = S[len(S)//2:]; nbs = [s[2] for s in h]; mx = [s[3][0] for s in S]
        e2 = [s[3][1] if len(s[3]) > 1 else 0 for s in S]
        drops = sum(1 for i in range(1, len(mx)) if mx[i] < mx[i-1] / 1.5 or e2[i] < e2[i-1] / 1.5)
        if min(nbs) >= 3 and max(nbs) <= 1.5 * max(1, min(nbs)) and mx[-1] >= 5 * max(1, mx[0]) and drops >= 2: lab = 'ENGINE?'
        elif nbs[-1] >= 2 * max(1, nbs[0]): lab = 'GROWLIST'
        else: lab = 'OTHER'
    print(m, lab, S[-1][1], S[-1][2], '/'.join(map(str, S[-1][3])))
