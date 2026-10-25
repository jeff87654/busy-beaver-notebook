import sys, subprocess, re
sys.path.insert(0, '..'); import idle  # noqa
MS = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
M = '1RB---_1RC1RD_0LD1LC_1RF0LE_0LG1LC_0RB0RG_0RA1LD'
tmpl = sys.argv[1]; res = {}
for b in range(1, int(sys.argv[3]) + 1 if len(sys.argv) > 3 else 25):
    for a in range(1, int(sys.argv[3]) + 1 if len(sys.argv) > 3 else 25):
        inp = tmpl.replace('B', str(b)).replace('A', str(a)) + '\n'
        p = subprocess.run([MS, M, '6', sys.argv[2] if len(sys.argv) > 2 else '400000', 'p50000', 'i'], input=inp, capture_output=True, text=True)
        out = p.stdout.strip().splitlines(); last = out[-1] if out else ''
        if last.startswith('H'): r = 'H'
        else:
            lst = [int(x) for l in out for x in re.findall(r'(?:100110 011001\^1 ){2,}', l) and [len(re.findall('100110 011001', l))]]
            n = max([len(re.findall(r'(110011\^1 001100\^1|100110\^1 011001\^1|011001\^1 100110\^1|001100\^1 110011\^1)', l)) for l in out] + [0])
            r = 'R' if n >= 5 else '?'
        res[(b, a)] = r
for b in range(1, int(sys.argv[3]) + 1 if len(sys.argv) > 3 else 25): print(f'b={b:2d} ' + ''.join(res[(b, a)] for a in range(1, int(sys.argv[3]) + 1 if len(sys.argv) > 3 else 25)))
