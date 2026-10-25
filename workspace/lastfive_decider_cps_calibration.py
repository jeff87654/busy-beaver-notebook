"""Verify the already-exported positive certificate; no upstream process needed.
Earlier subprocess calibration attempts timed out externally. The direct
execution subsequently exported this positive certificate; this script checks
its full closure independently and exercises malformed-certificate rejection.
"""
import json,copy
from pathlib import Path
from lastfive_decider_cps_verify import verify
p=Path('lastfive_decider_cps_certificates/cal_runaway_00.json')
c=json.loads(p.read_text())
out={'source_certificate':str(p),'independent_verification':verify(c),'negative_checks':[],
     'limitation':'Two earlier subprocess calibration attempts hit external 10-second timeouts. Direct execution exported this certificate. No BB2 or oscillator engine calibration is claimed.'}
for name in('missing initial configuration','missing blank-tail edges','machine changed to halt'):
 bad=copy.deepcopy(c)
 if name=='missing initial configuration':bad['configs']=[]
 elif name=='missing blank-tail edges':bad['edges']=[]
 else:bad['machine']='1RZ1RZ'
 try:verify(bad)
 except (AssertionError,ValueError)as e:out['negative_checks'].append({'mutation':name,'status':'rejected','reason':str(e)})
 else:raise AssertionError(('accepted malformed certificate',name))
Path('lastfive_decider_cps_calibration.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
