"""post6.py: post-pass for deep6 after deep.py (Idle, 2 lanes).
 S1 small-instance halting probe on ALL rows: nlp7v --small (2M macro) at K=2 and at the pilot K   -> small/K{k}.tsv
 S2 candidates C = FR>0 or SRs>=10 or nat_lg>=FASTTH (full 1e7) : nlp7v --life (1e7 macro) at K=2 and SRK -> life/K{k}.tsv
 S3 C: small probe 2e7 macro (10x) at K=2 and SRK                                               -> small20/K{k}.tsv
 S4 FR>0 and D>=4: HT = nlp7v --small --nolist 5e7 macro at K=2 and SRK                         -> ht/K{k}.tsv
 calibration: BB(7) champion + champ_231 through nlp7f 1e7 --k2 (cal_full.tsv)."""
import os, sys, subprocess, threading, time, glob, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import idle  # noqa
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
NL = os.path.abspath(os.path.join(H, '..', '..', 'nonlist')); V = os.path.join(NL, 'nlp7v.exe')
PIDS = os.path.join(H, '..', 'pids.txt'); lock = threading.Lock()
FASTTH = float(os.environ.get('FASTTH', '10.8'))
def rows(pat):
    for p in sorted(glob.glob(pat)):
        for l in open(p):
            if not l.startswith(('#', 'machine')): yield l.rstrip('\n').split('\t')
def launch(args):
    p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x40)
    with lock, open(PIDS, 'a') as f: f.write(f"{time.strftime('%F %H:%M')} {p.pid} deep6-post {' '.join(os.path.basename(a) for a in args[:6])}\n")
    p.wait()
def job(d, k, ms, macro, extra):
    os.makedirs(d, exist_ok=True); out = f'{d}/K{k}.tsv'
    if os.path.exists(out): return
    inp = f'{d}/K{k}.txt'; open(inp, 'w').write('\n'.join(sorted(ms)) + '\n')
    launch([V, inp, out + '.tmp', str(macro)] + extra + [f'--K={k}']); os.replace(out + '.tmp', out)
pil = {f[0]: f[1] for f in rows('pil/p*.tsv')}
full = {f[0]: f for f in rows('full/p*.tsv') if len(f) >= 17}
def fl(x):
    try: return float(x)
    except ValueError: return 0.0
if not os.path.exists('cal_full.tsv'):
    open('cal7.txt', 'w').write('1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF\n1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB\n')
    launch([os.path.join(NL, 'nlp7f.exe'), 'cal7.txt', 'cal_full.tsv', '10000000', '--k2'])
J1 = collections.defaultdict(set)
for m, k in pil.items(): J1['2'].add(m); J1[k].add(m)
with ThreadPoolExecutor(int(os.environ.get("W", "2"))) as ex: list(ex.map(lambda k: job('small', k, J1[k], 2000000, ['--small']), sorted(J1)))
C = [m for m, f in full.items() if int(f[16]) > 0 or int(f[6]) >= 10 or fl(f[3]) >= FASTTH or fl(f[11]) >= FASTTH]
J2 = collections.defaultdict(set)
for m in C: J2['2'].add(m); J2[full[m][8]].add(m)
with ThreadPoolExecutor(int(os.environ.get("W", "2"))) as ex:
    list(ex.map(lambda k: job('life', k, J2[k], 10000000, ['--life']), sorted(J2)))
    list(ex.map(lambda k: job('small20', k, J2[k], 20000000, ['--small']), sorted(J2)))
life = {}
for p in glob.glob('life/K*.tsv'):
    for f in rows(p):
        d = int(f[2]) if fl(f[3]) >= 0.5 else 0
        if d >= life.get(f[0], -1): life[f[0]] = d
J4 = collections.defaultdict(set)
for m in C:
    if int(full[m][16]) > 0 and life.get(m, 0) >= 4: J4['2'].add(m); J4[full[m][8]].add(m)
with ThreadPoolExecutor(int(os.environ.get("W", "2"))) as ex: list(ex.map(lambda k: job('ht', k, J4[k], 50000000, ['--small', '--nolist']), sorted(J4)))
print('post6 done: candidates', len(C), 'HT jobs', sum(len(v) for v in J4.values()), flush=True)
