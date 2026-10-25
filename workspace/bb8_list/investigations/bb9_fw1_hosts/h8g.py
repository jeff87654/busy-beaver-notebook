"""h8g.py OUT [WORKERS=2]: H8 + one new state I (9 states). Hook = an existing transition re-targeted to I (write/move kept)
or a free slot (D0 undefined, E0 never read) set to any write/move -> I; I0, I1 = any of 36 actions or halt.
Screen: hpc MODE-1 chain from the blank tape, b1 = 3 (and 5 when b1=3 survives >= 2 rounds), 10 rounds, 1e6 steps/round.
Output per machine: m, hook, halting round (or END/T) for b1=3 and b1=5. Resumable (skips machines in OUT)."""
import idle, subprocess, sys, os, re, itertools, threading
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); EXE = os.path.join(H, 'hpcw2.exe'); ENV = dict(os.environ, HPC_WMAX='3000', HPC_KMAX='20000')
BASE = '1RB1RG_0LC1LH_1LD1RC_---0LE_0RF0LA_0RA1LH_1RA0RC_1RA1LF'
ACTS = ['---'] + [w + m + t for w in '01' for m in 'LR' for t in 'ABCDEFGHI']
lock = threading.Lock()
def build(tr):
    return '_'.join(tr[(q, 0)] + tr[(q, 1)] for q in range(9))
def gen():
    parts = BASE.split('_'); tr = {}
    for q, p in enumerate(parts): tr[(q, 0)] = p[:3]; tr[(q, 1)] = p[3:]
    hooks = []
    for k, v in tr.items():
        if v != '---' and k != (4, 0): hooks.append((k, [v[:2] + 'I']))
    hooks.append(((3, 0), [w + m + 'I' for w in '01' for m in 'LR']))
    hooks.append(((4, 0), [w + m + 'I' for w in '01' for m in 'LR']))
    for k, opts in hooks:
        for o in opts:
            for i0 in ACTS:
                for i1 in ACTS:
                    t = dict(tr); t[k] = o; t[(8, 0)] = i0; t[(8, 1)] = i1
                    if '---' not in t.values(): continue
                    yield build(t), f'{chr(65 + k[0])}{k[1]}={o}'
def chain(m, b1):
    p = subprocess.Popen([EXE, m, 'R', 'C', '10', '11', '11', '0', '1', '0', '-', '0', 'A', str(b1), '10', '1000000', '6', '2', '1'],
                         stdout=subprocess.PIPE, text=True, creationflags=0x40, env=ENV)
    with lock:
        with open(os.path.join(H, 'pids.txt'), 'a') as f: f.write(f'{p.pid} hpcw h8g {m} b1={b1}\n')
    o = p.communicate()[0]
    h = re.search(r'R(\d+) HALT (\d+) state (\w) read (\d)', o); t = re.search(r'R(\d+) (?:TIMEOUT|WIDE)', o)
    nr = len(re.findall(r'^R\d+ \d+', o, re.M))
    return f'H{h[1]}:{h[3]}{h[4]}' if h else (f'T{t[1]}' if t else f'END{nr}')
def job(m, hook, out):
    a = chain(m, 3); b = '-'
    if a.startswith('H') and int(a[1:].split(':')[0]) >= 2 or a.startswith('T') and int(a[1:]) >= 2: b = chain(m, 5)
    with lock:
        with open(out, 'a') as f: f.write(f'{m}\t{hook}\t{a}\t{b}\n')
if __name__ == '__main__':
    out = sys.argv[1]; W = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    done = set(l.split('\t')[0] for l in open(out)) if os.path.exists(out) else set()
    ms = [x for x in gen() if x[0] not in done]
    print(len(ms), 'to do', flush=True)
    with ThreadPoolExecutor(W) as ex:
        for m, hk in ms: ex.submit(job, m, hk, out)
