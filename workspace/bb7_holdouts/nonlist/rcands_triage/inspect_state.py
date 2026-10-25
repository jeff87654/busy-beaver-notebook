import os, glob, time, shutil

NONLIST = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
BB7 = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'
TRIAGE = os.path.join(NONLIST, 'rcands_triage')

print("=== Files in nonlist ===")
for x in sorted(os.listdir(NONLIST)):
    fp = os.path.join(NONLIST, x)
    if os.path.isfile(fp):
        mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(fp)))
        print(f"{x:25s} {os.path.getsize(fp):12d}  {mt}")
    else:
        print(f"{x + '/':25s} <DIR>")

for sub in ['rchunks', 'rpil', 'rfull_in', 'rfull']:
    sp = os.path.join(NONLIST, sub)
    if os.path.exists(sp):
        files = sorted(os.listdir(sp))
        done_cnt = 0
        if sub in ('rpil', 'rfull'):
            for fn in files:
                if fn.endswith('.tsv'):
                    fp = os.path.join(sp, fn)
                    with open(fp, 'rb') as f:
                        f.seek(0, 2)
                        n = f.tell()
                        f.seek(max(0, n - 300))
                        if b'#summary' in f.read():
                            done_cnt += 1
        print(f"{sub:10s}: total={len(files)}, done={done_cnt}, first={files[0] if files else '-'}, last={files[-1] if files else '-'}")

print("\n=== Files in bb7_holdouts ===")
for root, dirs, files in os.walk(BB7):
    rel = os.path.relpath(root, BB7)
    if rel.count(os.sep) <= 2:
        exes = [f for f in files if f.endswith(('.exe', '.cpp', '.py'))]
        if exes:
            print(f"  {rel}: {exes}")
