"""lit.py: literal checks of family transitions with c04raw.exe (--target).  Words far->near, head B on the blank right."""
import subprocess, os, tempfile, random
HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, 'c04raw.exe')
TMP = os.path.join(HERE, '_tmp'); os.makedirs(TMP, exist_ok=True)
def tok(d): return '10' * d + '1'          # D(d) far->near
def T(t): return '11111100' * t
def D0(l, s, y, P, L, t):
    """D0 moment: l 1 (10)^(s+1) 1 (10)^y 011 (100)^P 1^L 11 (11111100)^t 1001 B>"""
    return l + '1' + '10' * (s + 1) + '1' + '10' * y + '011' + '100' * P + '1' * L + '11' + T(t) + '1001'
def check(start, target, steps=2 * 10**9, q='B'):
    fs = os.path.join(TMP, 's%d.txt' % os.getpid()); ft = os.path.join(TMP, 't%d.txt' % os.getpid())
    open(fs, 'w').write(start); open(ft, 'w').write(target)
    out = subprocess.run([EXE, '@file:%s:%s' % (fs, q), '--target', ft, '--steps', str(steps), '--max', '1'],
                         capture_output=True, text=True).stdout
    return out.startswith('MATCH'), out.strip()[:300]
def kmoments(start, steps, extra=()):
    fs = os.path.join(TMP, 's%d.txt' % os.getpid()); open(fs, 'w').write(start)
    return subprocess.run([EXE, '@file:%s:B' % fs, '--kmom', '--steps', str(steps), '--width', '100000'] + list(extra),
                          capture_output=True, text=True).stdout
