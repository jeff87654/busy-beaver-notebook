import sys,json,time,dataclasses
from pathlib import Path
sys.path[:0]=[str(Path('third_party/ligocki/Code').resolve()),str(Path('third_party/runtime_deps').resolve())]
import IO,Backtracking_Filter,Reverse_Engineer_Filter
rows=json.loads(Path('candidate_manifest.json').read_text())[8:];out=[]
for row in rows:
 start=time.monotonic();tm=IO.get_tm(row['machine'])
 result=Backtracking_Filter.backtrack(tm,200,300)
 r={'id':row['id'],'machine':row['machine'],'backtrack':dataclasses.asdict(result),'reverse_engineer':Reverse_Engineer_Filter.is_infinite(tm),'elapsed_seconds':time.monotonic()-start}
 out.append(r);Path('candidate_backtracking.json').write_text(json.dumps(out,indent=2));print(json.dumps(r),flush=True)
