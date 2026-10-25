"""pool.py LIST TAG A:r NWORK [extra d9f args...]: run d9f.py for every machine of LIST (IDLE priority, NWORK at a time).
Logs runs/TAG_<suffix>.log; summary line per machine appended to runs/TAG_summary.tsv."""
import sys, subprocess, os, time
lst, tag, Ar, nw = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]); extra = sys.argv[5:]
ms = [l.split()[0] for l in open(lst) if l.strip()]
here = os.path.dirname(os.path.abspath(__file__))
summ = os.path.join(here, 'runs', f'{tag}_summary.tsv')
done = set()
if os.path.exists(summ):
    done = {l.split('\t')[0] for l in open(summ)}
todo = [m for m in ms if m not in done]
run = {}
while todo or run:
    while todo and len(run) < nw:
        m = todo.pop(0); suf = m[56:].replace('-', 'x')
        lg = os.path.join(here, 'runs', f'{tag}_{suf}.log')
        p = subprocess.Popen([sys.executable, os.path.join(here, 'd9f.py'), m, Ar, '--log', lg, '--quiet'] + extra,
                             creationflags=subprocess.IDLE_PRIORITY_CLASS, stdout=subprocess.DEVNULL, stderr=open(lg + '.err', 'w'))
        run[p] = (m, lg, time.time())
    for p in list(run):
        if p.poll() is not None:
            m, lg, t0 = run.pop(p)
            last = open(lg).read().strip().split('\n')[-2:] if os.path.exists(lg) else ['?']
            with open(summ, 'a') as f:
                f.write(f'{m}\t{" || ".join(x[:200] for x in last)}\n')
    time.sleep(2)
