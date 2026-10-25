from kfam import run_next, predict
for b in range(0, 5):
    row = []
    for k in range(1, 26):
        ds = (1,) + (0,) * k
        r = run_next(ds, 0, b, N=10**6)
        p = predict(ds, 0, b)
        if r[0] == 'K' and r[2] == p: row.append('ok')
        elif r[0] == 'K': row.append('K%s' % (r[2],))
        else: row.append(r[0])
    print('b=%d' % b, ' '.join('%d:%s' % (k + 1, x) for k, x in enumerate(row)))
# blank reset ds=() a=0 : not representable; test ds=(1,) a=0 -> R2 to (); etc
