"""Check bounded runner status handling without altering upstream code."""
import json
from ligocki_runner import run_machine

if __name__=='__main__':
    cases = [
      ('halt','1RZ1RZ',{'timeout':5,'block_size':1}),
      ('infinite','1RA1RA',{'timeout':5,'block_size':1}),
      ('cutoff','1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA',
       {'timeout':5,'block_size':2,'max_loops':1}),
      ('cutoff','1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA',
       {'timeout':0.01}),
    ]
    results=[]
    for expected,machine,options in cases:
        result=run_machine(machine,**options)
        assert result['status']==expected,result
        results.append({'expected':expected,'result':result})
    assert results[-1]['result']['reason']=='external_wall_timeout'
    with open('audit_ligocki_status.json','w') as f:
        json.dump(results,f,indent=2)
    print('All four halt/infinite/loop-cutoff/wall-cutoff status checks passed.')
