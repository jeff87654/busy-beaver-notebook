"""screen.py LOG... : summarise zfg LEAF lines.  Per leaf: machine, outcome, jumps, first/max/last cleared-list length,
number of rises of the cleared list, class (growth = >= 3 rises and the max of the last third of the jumps
exceeds the max of the first third by > 20):
  GROW-HALT  halts on a slot read after >= 3 rises of the cleared list (grow-and-count candidate)
  GROW-LOOP  >= 3 rises, still running at the jump/step limit (f_(omega+1)-shape looper)
  GROW-T     >= 3 rises, then a segment timed out (unclassified)
  FLAT-*     fewer than 3 rises (H / T / J)"""
import sys, re
def expand(z):
    v = []
    for t in z.split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        elif t:
            v.append(int(t))
    return v
for fn in sys.argv[1:]:
    tape = None
    for l in open(fn):
        if l.startswith('  TAPE'):
            tape = l
        if not l.startswith('LEAF'):
            continue
        m = re.match(r'LEAF (\S+) (.*?) zeros=\[(.*?)\]', l)
        mach, head, z = m.groups()
        v = expand(z)
        rises = sum(1 for a, b in zip(v, v[1:]) if b > a + 2)
        n3 = max(1, len(v) // 3)
        grows = len(v) >= 6 and max(v[-n3:]) > max(v[:n3]) + 20 and rises >= 3
        if head.startswith('H '):
            o = 'H'; out = re.match(r'H (\S+) @J(\d+)', head); desc = f'H{out.group(1)}@J{out.group(2)}'
        elif head.startswith('T '):
            o = 'T'; desc = 'T@J' + re.match(r'T @J(\d+)', head).group(1)
        else:
            o = 'J'; desc = head
        cls = ('GROW-' + {'H': 'HALT', 'J': 'LOOP', 'T': 'T'}[o]) if grows else 'FLAT-' + o
        if o == 'T':
            seg = int(re.search(r'seg=(\d+)', head).group(1)) if 'seg=' in head else 0
            sub = 'CAP'
            if tape and seg >= 99999999:
                tm = re.search(r'head=([-+]\d+) \(from right end\) width=(\d+)', tape)
                hd, wd = int(tm.group(1)), int(tm.group(2))
                sub = 'RUN' if (wd > 1000000 or -hd > wd + 1000 or hd > 1000) else 'STRUCT'
            cls += '/' + sub
        tape = None
        print('\t'.join([mach, cls, desc, str(len(v)), str(v[0] if v else 0), str(max(v) if v else 0), str(v[-1] if v else 0), str(rises)]))
