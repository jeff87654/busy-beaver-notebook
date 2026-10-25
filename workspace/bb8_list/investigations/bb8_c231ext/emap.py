import idle, subprocess, sys, json
"""Exhaustion map: for machines in a jsonl/list, run K(a;0^n) -> first K-moment after H (or halt/END).
usage: emap.py machines.txt out.jsonl nlist alist_offsets maxsteps"""
ms = [l.split()[0] for l in open(sys.argv[1]) if l.strip()]
NS = eval(sys.argv[3]); OFF = eval(sys.argv[4]); MAXS = sys.argv[5]
with open(sys.argv[2], 'w', newline='\n') as f:
    for m in ms:
        res = {}
        for n in NS:
            for o in OFF:
                a = max((n + 2) // 3, 7) + o
                r = subprocess.run(['./follow.exe', m, MAXS, '1', 'first'], input='%d Z %d\n' % (a, n), capture_output=True, text=True)
                res['%d,%d' % (n, a)] = r.stdout.strip()
        f.write(json.dumps({'m': m, 'res': res}) + '\n'); f.flush()
