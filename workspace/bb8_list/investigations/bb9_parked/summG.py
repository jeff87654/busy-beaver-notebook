"""summG.py DIR TAG : one line per lkf log DIR/ID_TAG.txt
   jumps, end status, escalations (a cleared list k > 2 * every earlier k and k >= 1000 = an accumulator-sized rebuild),
   cleared-list maxima (digits), halting slot."""
import glob, os, re, sys
d, tag = sys.argv[1], sys.argv[2]
for f in sorted(glob.glob(os.path.join(d, '*_%s.txt' % tag))):
    id = os.path.basename(f)[:-len(tag) - 5]
    t = open(f).read()
    ks = [int(x) for x in re.findall(r'^J\d+ CL t=\d+ k=(\d+)', t, re.M)]
    nj = len(re.findall(r'^J\d', t, re.M))
    esc = 0; mx = 0; esc_at = []
    for i, k in enumerate(ks):
        if k >= 1000 and k > 2 * mx:
            esc += 1; esc_at.append(i + 1)
        mx = max(mx, k)
    m = re.search(r'^(HALT\S* \S+|STOP|END|SIMSTATE \S+|INF\?|Traceback)', t, re.M)
    st = m.group(1).replace('SIMSTATE ', '') if m else 'running?'
    print('%-5s J=%-4d %-18s esc=%-4d maxk=%s digits  ts=%s' % (id, nj, st, esc, len(str(mx)) if mx else 0,
          ','.join(sorted(set(re.findall(r'^J\d+ \S+ t=(\d+)', t, re.M)), key=int)[:12])))
