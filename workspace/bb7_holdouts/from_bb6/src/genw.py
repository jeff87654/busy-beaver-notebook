"""genw.py BASE OUT [MOD] [MAXS]: generic small worlds: snapshots of BASE's blank-tape run at 24 log-spaced times
(1e3..1e8), long blocks shrunk (shrink.py, residues mod MOD kept, 24 variants: 3 residue-keeping, 21 randomized), each run with haltcfg.exe (MAXS steps);
the halting configurations are the worlds. Idle priority (children inherit)."""
import sys, os, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import idle
D = os.path.dirname(os.path.abspath(__file__))
base, out = sys.argv[1], sys.argv[2]
mod = sys.argv[3] if len(sys.argv) > 3 else '12'; maxs = sys.argv[4] if len(sys.argv) > 4 else '10000000'
ts = sorted(set(int(10 ** (3 + 5 * i / 23)) for i in range(24)))
snaps = subprocess.run([os.path.join(D, 'snap.exe'), base] + [str(t) for t in ts], capture_output=True, text=True).stdout
tmp = out + '.snap'; open(tmp, 'w').write(snaps)
shr = subprocess.run([sys.executable, os.path.join(D, 'shrink.py'), tmp, mod, '24'], capture_output=True, text=True).stdout
p = subprocess.run([os.path.join(D, 'haltcfg.exe'), base, maxs], input=shr, capture_output=True, text=True)
# dedupe identical halting configs
seen, lines = set(), []
for l in p.stdout.splitlines():
    k = tuple(l.split()[2:])
    if k not in seen: seen.add(k); lines.append(l)
open(out, 'w').write('\n'.join(lines) + ('\n' if lines else ''))
nh = p.stderr.count('NOHALT')
print(f"{base}: snaps {len(snaps.splitlines())}, shrunk {len(shr.splitlines())}, halting {len(p.stdout.splitlines())} (distinct {len(lines)}), nohalt {nh}")
