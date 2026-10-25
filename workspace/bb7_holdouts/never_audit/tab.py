import json,glob,csv,sys
R='../reb7/'
ver={}
for row in csv.DictReader(open(R+'final_all_verdicts.tsv'),delimiter='\t'):
    ver[row['machine']]=row
runs={}
for f in glob.glob(R+'run_*.jsonl')+glob.glob(R+'mr_*.jsonl'):
    for l in open(f):
        try: d=json.loads(l)
        except: continue
        m=d.get('machine')
        if m: runs.setdefault(m,[]).append((f,d))
out=[]
for m,row in ver.items():
    if 'NEVER' not in row['verdict']: continue
    best=0;info=''
    for f,d in runs.get(m,[]):
        le=d.get('lit_exh') or []
        for e in le:
            try: best=max(best,int(e[2]))
            except: pass
        lk=d.get('last_K')
        if lk:
            try: best=max(best,int(lk[2]) if isinstance(lk[2],int) else len(lk[1]))
            except: pass
        if 'rules' in d: info=d.get('growth','')
    out.append((best,m,row['grade'],row['stage'],row['verdict'][:40],info,row['rules'][:60]))
out.sort(reverse=True)
for o in out[:int(sys.argv[1])]: print('\t'.join(map(str,o)))
print(len(out))
