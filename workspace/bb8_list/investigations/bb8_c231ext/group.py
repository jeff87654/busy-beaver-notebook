import idle, subprocess, collections, sys
ms = [l.strip() for l in open('cand55.txt') if l.strip()]
groups = collections.defaultdict(list)
for m in ms:
    sig = []
    for a, n in [(21, 20), (24, 20)]:
        r = subprocess.run(['./sweeps.exe', m, '400000000', '300'], input='%d Z %d\n' % (a, n), capture_output=True, text=True)
        lines = r.stdout.strip().split('\n')
        last = lines[-1] if not lines[-1].startswith('END') else (lines[-2] if len(lines) > 1 else lines[-1])
        sig.append('%d:%s' % (len(lines), last.split('|', 1)[-1][:160] if last.startswith('S') else last))
    groups[' || '.join(sig)].append(m)
for k, v in sorted(groups.items(), key=lambda x: -len(x[1])):
    print(len(v), k[:330])
    for m in v: print('     ', m)
