"""Bounded parameter portfolio for holdout candidates C01 through C06."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import time
from ligocki_runner import run_machine

if __name__=='__main__':
    started=time.monotonic()
    machines=Path('discovery_holdouts.txt').read_text().splitlines()[:6]
    results=[]
    solved=set()
    jobs=[]
    # Interleave candidates and sizes so every candidate gets broad coverage.
    for size in (3,4,2,6,8,12,1,10):
        for no_back in (False,True):
            for index,machine in enumerate(machines,1):
                jobs.append((index,machine,size,no_back,True))
    for index,machine in enumerate(machines,1):
        for no_back in (False,True):
            jobs.append((index,machine,4,no_back,False))

    def run(job):
        index,machine,size,no_back,recursive=job
        if time.monotonic()-started>260:
            return None
        if index in solved:
            return None
        result=run_machine(machine,timeout=4,max_loops=100000,
                           block_size=size,recursive=recursive,no_backsymbol=no_back)
        result.update(candidate=f'C{index:02}',portfolio_options={
            'block_size':size,'no_backsymbol':no_back,'recursive':recursive,
            'max_loops':100000,'timeout':4})
        return result

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(run,job) for job in jobs]
        for future in as_completed(futures):
            result=future.result()
            if result is None:continue
            results.append(result)
            if result['status'] in ('halt','infinite'):
                solved.add(int(result['candidate'][1:]))
                print(json.dumps({k:v for k,v in result.items() if k not in
                    ('upstream_log_tail','traceback','options')}),flush=True)
            output={'elapsed_seconds':time.monotonic()-started,
                    'coverage':'C01-C06 from discovery_holdouts.txt, 1-based',
                    'results':results,'solved_candidates':sorted(solved)}
            Path('candidate_audit.json').write_text(json.dumps(output,indent=2))
    print(json.dumps({'runs':len(results),'elapsed_seconds':time.monotonic()-started,
                      'solved_candidates':sorted(solved)}),flush=True)
