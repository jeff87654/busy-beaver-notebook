# summ.py: summarise jz enum / run outputs.  python summ.py FILES...
#  counts by kind; halters ranked by (number of big cascades, depth of the first big cascade list); holdouts listed
import sys, re, collections
C = collections.Counter(); halters = []; hold = []; nodes = 0
for fn in sys.argv[1:]:
    for l in open(fn, errors='replace'):
        if l.startswith('S '): nodes += int(l.split('nodes=')[1]); continue
        if l.startswith('C '): C['CYCLE ' + l.split()[3]] += 1; continue
        if not l.startswith(('T ', 'R ')): continue
        f = l.split(); v = f[3]
        if v == 'HALT':
            big = int(re.search(r' big=(\d+)', l).group(1)); C['HALT big=%d' % big] += 1
            sig = re.search(r' sigma=(\S+)', l).group(1)
            descs = l.split('|')[-1]
            deps = re.findall(r'X(\d+)=K\(B0=([^;]*);n=(\d+);dep=([^)]*)\)', descs)
            d0 = None
            if deps:
                dd = sorted(deps, key=lambda t: int(t[0]))[0]
                d0 = int(dd[3]) if dd[3].isdigit() else 10 ** 30
            halters.append((big, d0 or 0, l.strip()))
        elif v == 'CYCLE': C['CYCLE ' + f[4]] += 1
        else: C[v + ' ' + f[4][:30]] += 1; hold.append(l.strip())
print('nodes', nodes)
for k, n in sorted(C.items(), key=lambda t: -t[1]): print('%8d %s' % (n, k))
halters.sort(key=lambda t: (-t[0], -t[1]))
print('top halters:')
for big, d0, l in halters[:25]:
    f = l.split(); s = re.search(r' sigma=(\S+)', l).group(1)
    print('  big=%d d0=%s %s %s sigma=%s |%s' % (big, d0, f[1], f[2], s, l.split('|')[-1][:250]))
print('holdouts', len(hold))
