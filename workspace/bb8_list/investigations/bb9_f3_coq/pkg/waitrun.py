import idle
"""Wait up to T s for GitHub run RUN to finish; print failed/finished jobs.  python waitrun.py RUN T"""
import subprocess, sys, time, json
run, T = sys.argv[1], float(sys.argv[2]); t0 = time.time()
while True:
    try:
        out = subprocess.run(['gh', 'run', 'view', run, '--json', 'status,conclusion,jobs'], capture_output=True, text=True, cwd=r'C:\Users\jeffr\Downloads\bb9f3_wt').stdout
        d = json.loads(out)
    except Exception as e:
        d = None
    if d:
        bad = [j['name'] + ':' + str(j['conclusion']) for j in d['jobs'] if j['status'] == 'completed' and j['conclusion'] not in ('success', 'skipped')]
        if d['status'] == 'completed' or bad or time.time() - t0 > T:
            done = [j['name'] for j in d['jobs'] if j['status'] == 'completed']
            print('run', d['status'], d['conclusion'], '| failed:', bad, '| pending:', [j['name'] for j in d['jobs'] if j['status'] != 'completed'])
            break
    time.sleep(60)
