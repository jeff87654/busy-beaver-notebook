import sys, re
f = sys.argv[1]
pat = sys.argv[2]   # regex on the tape string (after loop number)
def short(t):
    def rep(m):
        e = m.group(2)
        if len(e) > 14: e = '~1e%d' % (len(e)-1)
        return m.group(1) + '^' + e
    return re.sub(r'(\d{3})\^(\d+)', rep, t)
prev = None
for line in open(f):
    m = re.match(r'\s*(\d+)\s+(000\^inf.*)$', line)
    if not m: continue
    t = m.group(2).strip()
    if re.search(pat, t):
        print(m.group(1), short(t)[:260])
