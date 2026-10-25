import idle, subprocess, re, collections
ms = [l.strip() for l in open('end0.txt') if l.strip()]
cls = collections.defaultdict(list)
out = open('end0cls.tsv', 'w', newline='\n')
for m in ms:
    r = subprocess.run(['./tapegrow.exe', m, '100000000'], input='21 Z 20\n', capture_output=True, text=True).stdout.strip().split('\n')
    last = r[-1]
    if not last.startswith('100000000'):
        c = 'OTHER:' + last
    else:
        sp = [tuple(map(int, re.search(r'span=\[(-?\d+),(-?\d+)\]', x).groups())) for x in r[-2:]]
        w1 = sp[0][1] - sp[0][0]; w2 = sp[1][1] - sp[1][0]
        ratio = w2 / w1
        side = 'L' if sp[1][0] < sp[0][0] and sp[1][1] == sp[0][1] else ('R' if sp[1][1] > sp[0][1] and sp[1][0] == sp[0][0] else 'both')
        c = 'sqrt' if 2.6 < ratio < 3.8 else ('lin' if ratio > 8 else ('log/slow' if ratio < 1.5 else 'mid'))
        c += '-' + side
    cls[c].append(m); out.write(m + '\t' + c + '\t' + r[-1] + '\n')
for c, v in cls.items(): print(c, len(v))
