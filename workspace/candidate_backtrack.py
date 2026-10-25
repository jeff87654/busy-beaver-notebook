import sys,json,time
from pathlib import Path
sys.path[:0]=['third_party/runtime_deps','third_party/ligocki/Code']
import Backtracking_Filter as B
from IO.TM_Record import parse_tm
machines=Path('discovery_holdouts.txt').read_text().splitlines()
results=[]
for i in (3,5,6):
 start=time.monotonic()
 result=B.backtrack(parse_tm(machines[i-1]),steps=500,max_width=20000)
 record={'candidate':f'C{i:02}','machine':machines[i-1],'result':vars(result),'elapsed_seconds':time.monotonic()-start}
 results.append(record)
 print(json.dumps(record),flush=True)
 Path('candidate_backtrack.json').write_text(json.dumps(results,indent=2))
