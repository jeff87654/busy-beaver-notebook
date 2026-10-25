import sys
def parse(path):
    raw = open(path, 'rb').read()
    txt = raw.decode('utf-16') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8', 'replace')
    out = {}
    for line in txt.splitlines():
        p = line.split('\t')
        if len(p) < 4:
            continue
        tab = {}
        for c in p[3:]:
            f = c.split(':')
            tab[int(f[0])] = (f[1].upper(), int(f[2]), int(f[3]), int(f[4]), int(f[5]))
        out[p[2]] = tab
    return out
a = parse(sys.argv[1]); b = parse(sys.argv[2])
for tm in a:
    ta, tb = a[tm], b[tm]
    diff = [k for k in ta if ta[k] != tb[k]]
    first = diff[:12]
    print(tm, 'ndiff=%d/%d' % (len(diff), len(ta)), 'first diffs:', [(k, ta[k][:2], tb[k][:2]) for k in first])
