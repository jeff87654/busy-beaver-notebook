"""Batch event probe with hyb10b (one process per worker, Idle).
python bprobe.py MACHFILE OUT.tsv WORKERS MAXSTEPS SPEC
SPEC is a python expression giving a list of (tag, left_list, X, Z, k, r, t) tuples (evaluated with d2map in scope).
Output: machine tag left X Z k r kind steps nleft leftitems."""
import subprocess, sys, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import d2map
LOW = subprocess.IDLE_PRIORITY_CLASS
EXE = str(Path(__file__).resolve().parent / 'src' / 'hyb10b.exe')
def ntok(items):
    n = 0
    for t in items:
        g = re.fullmatch(r'(\d+)\*(\d+)', t)
        n += int(g.group(2)) if g else 1
    return n
def left_part(body):
    out = []
    for i, t in enumerate(body.split()):
        if i > 0 and re.fullmatch(r'0\*([5-9]|\d\d+)', t): break
        if t.startswith('<') or t.startswith('['): break
        out.append(t)
    return out
def main():
    mf, out, W, MAXS, spec = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
    ms = [l.split()[0] for l in Path(mf).read_text().splitlines() if l.strip()]
    pts = eval(spec)
    jobs = []
    for mi, m in enumerate(ms):
        for pi, (tag, left, X, Z, k, r, t) in enumerate(pts):
            w = d2map.word(left, X, k, r, t, Z)
            jobs.append((f'{mi}:{pi}', f'{mi}:{pi} {m} @{w} {len(w)} A {MAXS} -q A'))
    tmp = out.parent / (out.stem + '_jobs'); tmp.mkdir(exist_ok=True)
    def run(i):
        f = tmp / f'j{i}.txt'; f.write_text('\n'.join(j[1] for j in jobs[i::W]) + '\n')
        r = subprocess.run([EXE, str(f)], capture_output=True, text=True, creationflags=LOW)
        if r.returncode: raise SystemExit(f'hyb10b failed: {r.stderr[:300]}')
        return r.stdout
    with ThreadPoolExecutor(W) as ex: res = ''.join(ex.map(run, range(W)))
    got = {}
    lab = None
    for line in res.splitlines():
        if line.startswith('### '): lab = line[4:]; continue
        if lab and line[:1] in 'JHTNM' and ' | ' in line or (lab and line[:1] == 'T'):
            got[lab] = line; lab = None
    missing = [j[0] for j in jobs if j[0] not in got]
    if missing: raise SystemExit(f'{len(missing)} jobs without a stop line, e.g. {missing[:5]}')
    with out.open('w') as f:
        for lab, _ in jobs:
            mi, pi = map(int, lab.split(':'))
            tag, left, X, Z, k, r, t = pts[pi]
            head, _, body = got[lab].partition(' | ')
            hf = head.split()
            lp = left_part(body)
            f.write(f'{ms[mi]}\t{tag}\t{",".join(map(str, left))}\t{X}\t{Z}\t{k}\t{r}\t{hf[0]}\t{hf[1]}\t{ntok(lp)}\t{" ".join(lp)[:300]}\n')
    print('jobs', len(jobs))
main()
