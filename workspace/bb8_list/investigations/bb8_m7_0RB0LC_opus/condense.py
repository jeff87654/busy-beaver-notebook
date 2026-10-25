"""condense a COMPACT shadow log: collapse periodic stretches of event shapes"""
import sys, re
lines = open(sys.argv[1]).read().split('\n')
evs = []
i = 0
while i < len(lines):
    if lines[i].startswith('EV'):
        a = lines[i]; b = lines[i+1].strip() if i+1 < len(lines) else ''
        evs.append((a, b)); i += 2
    else: i += 1
def shape(s):
    s = re.sub(r'\.\.[^|]*\|', '..Q |', s)
    return re.sub(r'\d+', '#', s)
out = []; k = 0
while k < len(evs):
    found = False
    for p in (1, 2, 3, 4, 6):
        if k + 2*p <= len(evs) and all(shape(evs[k+j][0]) == shape(evs[k+p+j][0]) for j in range(p)):
            m = k + p
            while m + p <= len(evs) and all(shape(evs[m+j][0]) == shape(evs[k+j][0]) for j in range(p)): m += p
            reps = (m - k) // p
            out.append(f'  [cycle of {p} events x {reps}: {evs[k][0][:150]} ... -> {evs[m-1][1][:150]}]')
            k = m; found = True; break
    if not found:
        out.append(evs[k][0][:200]); out.append('     ' + evs[k][1][:200]); k += 1
print('\n'.join(out))
