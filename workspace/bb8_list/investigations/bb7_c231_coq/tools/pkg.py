import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq')
import idle
"""Build a clean package dir pkg/ from coq/ with descriptive names, compile everything in order (Idle, max 1 coqc,
memory guard via tools/cq.py logic), run both probes.  python tools/pkg.py"""
import re, shutil, subprocess, time, os
from pathlib import Path
W = Path(__file__).resolve().parents[1]
SRC = W / 'coq'; PKG = W / 'pkg'
ren = {'BB72': 'BB72', 'Individual72': 'Individual72', 'Clr': 'Clr', 'Bound': 'Bound', 'Bound3': 'Bound3',
       'T1': 'C231_rules1', 'T2': 'C231_rules2', 'T3': 'C231_rules3', 'T4': 'C231_init', 'T5': 'C231_clear',
       'T6': 'C231_run', 'M231': 'C231_main', 'probe': 'probe231',
       'U1': 'C232_rules1', 'U2': 'C232_rules2', 'U3': 'C232_rules3', 'U4': 'C232_init', 'U5': 'C232_clear',
       'U6': 'C232_run', 'M232': 'C232_main', 'probe232': 'probe232'}
order = ['BB72', 'Individual72', 'Clr', 'Bound', 'Bound3', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'M231', 'probe',
         'U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'M232', 'probe232']
if PKG.exists(): shutil.rmtree(PKG)
PKG.mkdir()
def fix(m):
    return 'Require ' + m.group(1) + ' ' + ' '.join(ren.get(x, x) for x in m.group(2).split()) + '.'
for n in order:
    s = (SRC / (n + '.v')).read_text()
    s = re.sub(r'Require (Import|Export) ([^.]*)\.', fix, s)
    (PKG / (ren[n] + '.v')).write_bytes(s.replace('\r\n', '\n').encode())
(PKG / '_CoqProject').write_text('-Q ../../bb9_f3_coq/ext/busycoq/verify BusyCoq\n-Q . BB8\n' + '\n'.join(ren[n] + '.v' for n in order) + '\n')
(PKG / 'build_order.txt').write_text('\n'.join(ren[n] + '.v' for n in order) + '\n')
if '--nobuild' in sys.argv: sys.exit(0)
BUSY = W.parent / 'bb9_f3_coq' / 'ext' / 'busycoq' / 'verify'
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
log = open(PKG / 'compile_clean.log', 'w')
t00 = time.time()
for n in order:
    f = ren[n] + '.v'; t0 = time.time()
    out = PKG / (ren[n] + '.out')
    with open(out, 'w') as o:
        p = subprocess.Popen([COQC, '-Q', str(BUSY), 'BusyCoq', '-Q', '.', 'BB8', f], cwd=PKG, stdout=o, stderr=subprocess.STDOUT,
                             creationflags=subprocess.IDLE_PRIORITY_CLASS)
        with open(W / 'pids.txt', 'a') as pf: pf.write('%d coqc pkg/%s %s\n' % (p.pid, f, time.strftime('%Y-%m-%d %H:%M:%S')))
        rc = p.wait()
    log.write('%s exit %s %.1fs\n' % (f, rc, time.time() - t0)); log.flush()
    print(f, rc, '%.1fs' % (time.time() - t0), flush=True)
    if rc != 0: print(open(out).read()[-2000:]); sys.exit(1)
log.write('total %.1fs\n' % (time.time() - t00)); log.close()
for pr in ('probe231', 'probe232'):
    shutil.copy(PKG / (pr + '.out'), PKG / (pr + '.log'))
    print(open(PKG / (pr + '.log')).read()[:1500])
