import sys, os, glob, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

HERE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_7state_fw1_redirects'
DL2_DIR = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl2_out'
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\nested_detector\dlscan3.exe'

files = sorted(glob.glob(os.path.join(DL2_DIR, 'c*.tsv')))
new_files = [f for f in files if int(os.path.basename(f)[1:6]) >= 209]
print(f"Found {len(new_files)} chunks >= c00209: {[os.path.basename(f) for f in new_files]}")

machines = []
for f in new_files:
    with open(f, 'r', encoding='utf-8', errors='replace') as fp:
        for line in fp:
            line = line.strip()
            if not line or line.startswith('machine') or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) >= 2 and parts[1] in ('DEEP-LIST', 'DEEP-PREFIX', 'CHECK', 'DL2'):
                machines.append(parts[0])
            elif len(parts) == 1 and '_' in parts[0]:
                machines.append(parts[0])
            elif '_' in parts[0]:
                machines.append(parts[0])

machines = sorted(set(machines))
print(f"Total unique machines in c00209+: {len(machines)}")

inp = os.path.join(HERE, 'c209_plus_machines.txt')
out = os.path.join(HERE, 'c209_plus_dl3.tsv')
log = os.path.join(HERE, 'c209_plus_dl3.log')

with open(inp, 'w') as fp:
    for m in machines:
        fp.write(m + '\n')

if machines:
    with open(log, 'w') as lf:
        p = subprocess.Popen([EXE, inp, out], creationflags=0x40, stdout=lf, stderr=subprocess.STDOUT)
        with open(os.path.join(HERE, 'pids.txt'), 'a') as pf:
            pf.write(f"dlscan3 {p.pid}\n")
        p.wait()
    print("dlscan3 return code:", p.returncode)
    with open(out, 'r', encoding='utf-8', errors='replace') as fp:
        lines = [l.rstrip('\r\n') for l in fp if l.strip()]
    by_grade = {}
    for l in lines[1:]:
        if l.startswith('#'):
            print(l)
            continue
        parts = l.split('\t')
        g = parts[3] if len(parts) > 3 else '?'
        by_grade.setdefault(g, []).append(parts)
    for g, items in sorted(by_grade.items()):
        if g not in ('LOOPER', 'NOBOUNDARY', 'SAFE'):
            print(f"\n=== Grade {g} ({len(items)}) ===")
            for it in items:
                print("  " + "\t".join(it))
