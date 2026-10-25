"""summB.py DIR : per lead, per B: outcome@jumps/max cleared list (pkf/lkf logs named ID_TAG.txt)"""
import glob, re, collections, os, sys
res = collections.defaultdict(dict)
for f in glob.glob(os.path.join(sys.argv[1], '*.txt')):
    id, B = os.path.basename(f)[:-4].rsplit('_', 1)
    t = open(f).read()
    nj = len(re.findall(r'^J\d', t, re.M))
    m = re.search(r'^(HALT\S* \S+|STOP|END|SIMSTATE \S+|INF\?)', t, re.M)
    z = [int(x) for x in t.split('zeros:')[1].split()] if 'zeros:' in t else [int(x) for x in re.findall(r' k=(\d+)', t)]
    out = (m.group(1).replace('HALT ', 'H').replace('SIMSTATE ', '') if m else '?')
    res[id][B] = '%s@%d/k%d' % (out, nj, max(z) if z else -1)
for id in sorted(res):
    print(id, ' '.join('%s:%s' % (B, res[id][B]) for B in sorted(res[id], key=lambda x: (len(x), x))))
