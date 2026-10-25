import sys, os, glob
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

dl2_dir = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl2_out'
files = sorted(glob.glob(os.path.join(dl2_dir, 'c*.tsv')))
print(f"Found {len(files)} files in dl2_out")

champs = {}
all_grades = {}
for p in files:
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        if not any(l.startswith('#summary') for l in lines[-5:]):
            continue
        for line in lines:
            if line.startswith('#') or line.startswith('machine'):
                continue
            parts = line.rstrip('\r\n').split('\t')
            if len(parts) >= 4 and parts[3] != '-':
                g = parts[3]
                all_grades[g] = all_grades.get(g, 0) + 1
                if g == 'CHAMPION':
                    champs[parts[0]] = ('dl2_out/' + os.path.basename(p), line.rstrip('\r\n'))
    except Exception as e:
        pass

for extra in [
    r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\hits_triage7.tsv',
    r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_triage7\out.tsv',
    r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits\out.tsv',
    r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\prefilter\hits_dl2_1M.tsv',
]:
    if os.path.exists(extra):
        with open(extra, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.startswith('#') or line.startswith('machine'):
                    continue
                parts = line.rstrip('\r\n').split('\t')
                if len(parts) >= 4 and parts[3] == 'CHAMPION':
                    if parts[0] not in champs:
                        champs[parts[0]] = (os.path.basename(extra), line.rstrip('\r\n'))

print("dl2_out grades:", all_grades)
print(f"\nTotal unique CHAMPION machines found: {len(champs)}")
for m in sorted(champs.keys()):
    src, line = champs[m]
    print(f"[{src}] {line}")
