import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
import subprocess, time, os

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ.get('PATH', '')
HERE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_record_hunt'
PIDS = os.path.join(HERE, 'pids.txt')
EXE = os.path.join(HERE, 'audit7.exe')
IN_TSV = os.path.join(HERE, 'mult_all.tsv')
OUT_TSV = os.path.join(HERE, 'audit_out.tsv')

# Also append the 10 LEAVES-TEMPLATE CHAMPION rows from rank_all.tsv if not already in mult_all.tsv
seen = set(line.split('\t')[0] for line in open(IN_TSV, encoding='utf-8'))
with open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\rank\rows_all.tsv', encoding='utf-8') as f, open(IN_TSV, 'a', encoding='utf-8') as out:
    for line in f:
        parts = line.rstrip('\n').split('\t')
        if len(parts) >= 6 and parts[0] not in seen:
            seen.add(parts[0])
            out.write('\t'.join(parts[:6]) + '\trows_all.tsv\n')

p = subprocess.Popen([EXE, IN_TSV, OUT_TSV], creationflags=getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0x40))
with open(PIDS, 'a', encoding='utf-8') as pf:
    pf.write(f"{p.pid}\t{time.strftime('%Y-%m-%d %H:%M:%S')}\taudit7.exe\n")
ret = p.wait()
print("audit7 exited with", ret)
