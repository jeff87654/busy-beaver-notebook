import idle, subprocess, math, sys
ms = [l.split('\t')[0] for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\low34.txt') if l.strip()]
for m in ms:
    o = subprocess.run([r'.\rec.exe', m, sys.argv[1], '100000'], capture_output=True, text=True, creationflags=0x40).stdout.splitlines()
    ev = []
    for ln in o:
        f = ln.split()
        if len(f) == 3 and f[0].isdigit(): ev.append((int(f[0]), len(f[2]), f[2]))
    end = o[-1]
    if len(ev) < 10: print(m, 'few events', end); continue
    a, b = ev[len(ev)//2], ev[-1]
    slope = (b[1] - a[1]) / (math.log2(b[0]) - math.log2(a[0]))
    print('%s span=%d slope=%.2f cells/doubling  last=%s  %s' % (m, b[1], slope, b[2][:40] + '..' + b[2][-20:], end[:30]))
