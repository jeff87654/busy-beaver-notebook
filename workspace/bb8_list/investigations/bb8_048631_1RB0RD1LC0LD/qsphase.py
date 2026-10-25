import sys, re
f = sys.argv[1]
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
prev = None
for line in open(f):
    m = re.match(r'\s*(\d+)\s+(000\^inf.*)$', line)
    if not m: continue
    loop = int(m.group(1))
    if loop < lo: continue
    toks = m.group(2).split()
    shape = []
    vals = []
    for t in toks:
        mm = re.match(r'^(\d+)\^(.*)$', t)
        if mm and mm.group(2) != 'inf':
            shape.append(mm.group(1))
            e = mm.group(2)
            if e.startswith('(~'):
                vals.append(e)
            else:
                vals.append(e if len(e) < 12 else '~1e%d' % (len(e)-1))
        else:
            shape.append(t); vals.append('')
    sh = ' '.join(shape)
    if sh != prev:
        out = []
        for s_, v in zip(shape, vals):
            out.append(s_ + ('^' + v if v else ''))
        print(loop, ' '.join(out))
    prev = sh
