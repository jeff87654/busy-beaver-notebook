"""Complete and independently triage the two initial 8-state holdout shards."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import time

from ligocki_runner import CODE, ROOT, run_machine


if __name__ == '__main__':
    start = time.monotonic()
    with open(ROOT/'audit_ligocki_bb5.json',encoding='utf-8') as f:
        calibration = json.load(f)['results'][0]
    assert calibration['status']=='halt'
    assert calibration['steps']=={'kind':'integer','decimal':'47176870'}
    assert calibration['ones']=={'kind':'integer','decimal':'4098'}
    records = []
    for filename in ('pilot8_243308/holdouts_243308.txt',
                     'pilot8_202609/holdouts_202609.txt'):
        for number,line in enumerate((ROOT/filename).read_text().splitlines(),1):
            original = line.strip()
            if not original or original=='stopped':
                continue
            assert original.count('---')==1, original
            records.append({'origin_file':filename,'origin_line':number,
                'original_partial_machine':original,
                'completion':'replace the sole --- with 1RZ',
                'machine':original.replace('---','1RZ')})
    assert len(records)==21
    options = {'workers':2,'timeout_seconds':10,'max_loops':10000,
               'block_size':'automatic','block_finder_loops':1000,'recursive':False}
    hashes = {name:hashlib.sha256((CODE/name).read_bytes()).hexdigest()
              for name in ('Quick_Sim.py','Macro/Simulator.py','Macro/Proof_System.py',
                           'Macro/Turing_Machine.py','Time_Limit.py')}
    output = {'configuration':options,'calibration':calibration,
              'source_sha256':hashes,'source_modified':False,
              'statuses_note':'Timeouts and simulation limits are unresolved cutoffs; errors are separate.',
              'results':[]}
    with ThreadPoolExecutor(max_workers=2) as pool:
        pending = {pool.submit(run_machine,r['machine'],timeout=10,max_loops=10000):r
                   for r in records}
        for future in as_completed(pending):
            record = pending[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {'machine':record['machine'],'status':'error',
                          'reason':'wrapper_exception','error':repr(exc)}
            result.update(record)
            output['results'].append(result)
            output['elapsed_seconds'] = time.monotonic()-start
            output['counts'] = {status:sum(r['status']==status for r in output['results'])
                                for status in ('halt','infinite','cutoff','undefined','error')}
            (ROOT/'discovery_triage.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
            print(json.dumps({'completed':len(output['results']),'status':result['status'],
                              'reason':result['reason'],'origin':record['origin_file'],
                              'line':record['origin_line'],
                              'steps':result.get('steps'),'ones':result.get('ones')}),flush=True)
    print(json.dumps({'counts':output['counts'],'elapsed_seconds':output['elapsed_seconds']}),flush=True)
