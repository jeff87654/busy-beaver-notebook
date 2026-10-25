import idle, subprocess, sys, json
"""Stage-1 behaviour scan: each nontrivial extension (H0 = halt), n=20, several a, literal follow."""
A = [int(x) for x in sys.argv[1].split(',')]; MAXS = sys.argv[2]; out = sys.argv[3]
ms = [l.split('\t') for l in open('ext8.txt').read().split('\n') if l]
ms = [(m, b) for m, b in ms if m.split('_')[7].startswith('---')]
with open(out, 'w', newline='\n') as f:
    for m, b in ms:
        rec = {'m': m, 'base': b, 'runs': {}}
        for a in A:
            r = subprocess.run(['./follow.exe', m, MAXS, '40'], input='%d Z 20\n' % a, capture_output=True, text=True)
            rec['runs'][a] = r.stdout.strip().split('\n')
        f.write(json.dumps(rec) + '\n'); f.flush()
