# runjobs.py JOBS.json OUT PAR : jobs = [[machine, label, args]], pkf7.exe, real PIDs -> ../pids.txt
import subprocess, sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); EXE = os.path.join(os.path.dirname(HERE), 'tools', 'pkf7b.exe')
jobs = json.load(open(sys.argv[1])); out = open(sys.argv[2], 'a'); par = int(sys.argv[3]); live = []
while jobs or live:
    while jobs and len(live) < par:
        m, lab, a = jobs.pop(0); tmp = open(sys.argv[2] + '.tmp_' + lab.replace(' ', '_').replace('=', ''), 'w+')
        p = subprocess.Popen([EXE, m] + a, stdout=tmp, stderr=subprocess.STDOUT, text=True, creationflags=0x40)
        open(os.path.join(os.path.dirname(HERE), 'pids.txt'), 'a').write('%s %d z1/runjobs %s\n' % (time.strftime('%m-%d %H:%M:%S'), p.pid, lab))
        live.append((p, lab, tmp))
    for x in live[:]:
        p, lab, tmp = x
        if p.poll() is None: continue
        live.remove(x); tmp.seek(0)
        ls = [l.split(' used=')[0].replace(' step=', ' s=') + (' |' + l.split('|', 1)[1] if '|' in l and ' used=' in l else '') if l.startswith('J') else l for l in tmp]
        out.write('== %s\n%s' % (lab, ''.join(x if x.endswith('\n') else x + '\n' for x in ls))); out.flush(); tmp.close(); os.remove(tmp.name)
    time.sleep(0.5)
