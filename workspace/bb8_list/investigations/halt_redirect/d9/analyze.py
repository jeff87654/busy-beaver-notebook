"""analyze.py LOG...: per follower log: result, stages, I0 uses, deepest borrow (depth = zero digits right of the
rightmost token the jump decreased, +1), number of deep borrows (depth >= DEEP), rebuild events (LOOK), last K."""
import sys, re
DEEP = 300
def expand(s):
    v = []
    for t in s.split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        else:
            v.append(int(t))
    return v
def parse_list(s):
    s = s.split('|')[0]
    return expand(s)
def one(path):
    res = 'RUNNING'; ns = 0; i0 = 0; maxd = (0, -1); ndeep = 0; looks = 0; lastK = ''; K = None; maxn = (0, -1)
    deep_stages = []
    for l in open(path):
        m = re.match(r'(\d+) (K|J): (.*)', l)
        if l.startswith('RESULT'):
            res = l.split()[1] + ' ' + l.split()[2]; continue
        if ' LOOK:' in l: looks += 1
        if not m: continue
        s = int(m.group(1)); ns = s
        body = m.group(3)
        if m.group(2) == 'K':
            if ' I0 ' in body + ' ': i0 += 1
            lst = body.split(' | ')[0]
            K = expand(lst) if lst.strip() else []
            lastK = f'{s} {body[:150]}'
            nn = re.search(r' n=(\d+)', body)
            if nn and int(nn.group(1)) > maxn[0]: maxn = (int(nn.group(1)), s)
        else:
            if K is None: continue
            after = body.split('-> ', 1)[1].split(' | ')[0]
            J = expand(after) if after.strip() else []
            # align right ends; jump keeps length unless tokens consumed; find rightmost index where J < K
            # depth of the borrow = number of 1-tokens right of that position in K
            d = 0
            n = min(len(K), len(J))
            for k in range(1, n + 1):
                if J[-k] != K[-k]:
                    # depth: count ones right of position -k in K
                    pos = len(K) - k
                    d = max(d, sum(1 for x in K[pos + 1:] if x == 1) + 1)
            # also: if J is shorter, the borrow reached further left
            if len(J) < len(K):
                pos = len(K) - len(J) - 1
                d = max(d, sum(1 for x in K[max(pos, 0):] if x == 1) + 1)
            if d > maxd[0]: maxd = (d, s)
            if d >= DEEP:
                ndeep += 1
                if len(deep_stages) < 6: deep_stages.append((s, d))
    return dict(res=res, ns=ns, i0=i0, maxd=maxd, ndeep=ndeep, deep=deep_stages, looks=looks, maxn=maxn, lastK=lastK)
if __name__ == '__main__':
    for p in sys.argv[1:]:
        r = one(p)
        name = re.sub(r'.*_(\w{6}_\w{6})\.log$', r'\1', p)
        print(f"{name}\t{r['res']}\tst={r['ns']}\tI0={r['i0']}\tmaxdepth={r['maxd'][0]}@{r['maxd'][1]}\tdeep={r['ndeep']} {r['deep']}\tlooks={r['looks']}\tmaxn={r['maxn'][0]}@{r['maxn'][1]}\t{r['lastK']}")
