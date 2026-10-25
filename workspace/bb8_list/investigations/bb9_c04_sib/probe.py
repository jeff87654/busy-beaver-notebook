"""probe.py : run ONE event of an n1-engine machine from a B-form start (msim2.exe --start ... --events 1).
  python probe.py "cfg|A" [TM]      prints the resulting B-form (or HALT/STOP)
  as a module: ev(cfg_tokens_list, A, tm=X1) -> (tokens_list, A) or a string"""
import subprocess, sys, os
X1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_0RG1LD_1RH1LG_1LC0RG_---0RA'
EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.environ.get('PROBE_EXE', 'msim2.exe'))
LAST_CTX = ''
def parse(s):
    s = s.strip().strip('[]'); f, A = s.split('|'); ts = []
    for x in f.split():
        if '^' in x: v, c = x.split('^'); ts += [int(v)] * int(c)
        else: ts.append(int(x))
    return ts, int(A)
def rle(ts):
    out = []; i = 0
    while i < len(ts):
        j = i
        while j < len(ts) and ts[j] == ts[i]: j += 1
        out.append(str(ts[i]) if j - i == 1 else '%d^%d' % (ts[i], j - i)); i = j
    return ' '.join(out)
def ev(ts, A, tm=X1, maxseg=3e10):
    cfg = rle(ts) + '|' + str(A)
    o = subprocess.run([EXE, tm, '--start', cfg, '--events', '1', '--maxseg', str(maxseg), '--view', '100000'], capture_output=True, text=True).stdout
    global LAST_CTX
    LAST_CTX = ''
    for l in o.splitlines():
        if l.startswith('E0CTX') and not LAST_CTX: LAST_CTX = l
    for l in o.splitlines():
        if l.startswith('EV1'):
            right = l.split(' -> ', 1)[1].rsplit(' seg ', 1)[0]
            return parse(right) + (int(l.rsplit(' seg ', 1)[1]),)
        if l.startswith('HALT') or l.startswith('STOP'): return l
    return o
if __name__ == '__main__':
    ts, A = parse(sys.argv[1]); r = ev(ts, A, sys.argv[2] if len(sys.argv) > 2 else X1)
    print(r if isinstance(r, str) else '[%s | %d] seg %d' % (rle(r[0]), r[1], r[2]))
