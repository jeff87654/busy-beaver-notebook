"""taint.py A LOG...: find the first stage where the A token (leftmost token / leftmost (10)^n of the far bits, value
within A +- 400) is gone (borrowed or unpacked); count deep borrows (depth >= 300) before and after that stage."""
import sys, re
sys.path.insert(0, '.')
from analyze import expand
A = int(sys.argv[1]); DEEP = 300
def leftmost(body):
    m = re.search(r' far=(\S+)', body)
    if m:
        f = m.group(1); g = re.match(r'1?\(10\)\^(\d+)', f)
        if not g: return -1
        digs = g.group(1)
        for k in range(1, min(len(digs), 7) + 1):   # cfar output is ambiguous: (10)^n is followed by raw bits
            v = int(digs[:k])
            if A - 400 <= v <= A + 400: return v
        return int(digs[:min(len(digs), 6)])
    lst = body.split(' | ')[0].split()
    if not lst: return -1
    return int(lst[0].split('^')[0])
for p in sys.argv[2:]:
    gone = None; pre = post = 0; res = '?'; K = None; deepstages = []
    for l in open(p):
        if l.startswith('RESULT'): res = ' '.join(l.split()[1:3])
        m = re.match(r'(\d+) (K|J): (.*)', l)
        if not m: continue
        s = int(m.group(1)); body = m.group(3)
        if m.group(2) == 'K':
            lm = leftmost(body)
            if gone is None and not (A - 400 <= lm <= A + 400): gone = s
            K = expand(body.split(' | ')[0]) if body.split(' | ')[0].strip() else []
        elif K is not None:
            J = expand(body.split('-> ', 1)[1].split(' | ')[0])
            d = 0
            for k in range(1, min(len(K), len(J)) + 1):
                if J[-k] != K[-k]:
                    pos = len(K) - k; d = max(d, sum(1 for x in K[pos + 1:] if x == 1) + 1)
            if d >= DEEP:
                if gone is None: pre += 1
                else: post += 1
    name = re.sub(r'.*_(\w{6}_\w{6})\.log$', r'\1', p)
    print(f'{name}\t{res}\tAgone@{gone}\tdeep_before={pre}\tdeep_after={post}')
