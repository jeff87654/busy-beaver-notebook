import sys, os, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

HERE = os.path.dirname(os.path.abspath(__file__))
exe = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\nested_detector\dlscan3.exe'
inp = os.path.join(HERE, 'new_machines.txt')
out = os.path.join(HERE, 'new_dl3_out.tsv')
log = os.path.join(HERE, 'new_dl3.log')

with open(log, 'w') as lf:
    p = subprocess.Popen([exe, inp, out], creationflags=0x40, stdout=lf, stderr=subprocess.STDOUT)
    with open(os.path.join(HERE, 'pids.txt'), 'a') as pf:
        pf.write(f"dlscan3 {p.pid}\n")
    p.wait()

print("dlscan3 finished with return code:", p.returncode)
with open(out, 'r', encoding='utf-8', errors='replace') as f:
    lines = [l.rstrip('\r\n') for l in f if l.strip()]

print(f"Total output lines: {len(lines)}")
by_grade = {}
for l in lines[1:]:
    parts = l.split('\t')
    g = parts[3] if len(parts) > 3 else '?'
    by_grade.setdefault(g, []).append(parts)

for g, items in sorted(by_grade.items()):
    print(f"  {g}: {len(items)}")

for g in ('W1-HALTER', 'W1-HALT?', 'W1-LOOPER', 'MULTI', 'R4-SOME', 'REBUILD', 'HALT-SOME', 'CHAMPION', 'HALT?'):
    if g in by_grade:
        print(f"\n=== NEW batch Grade: {g} ({len(by_grade[g])}) ===")
        for parts in by_grade[g]:
            print("  " + "\t".join(parts))
