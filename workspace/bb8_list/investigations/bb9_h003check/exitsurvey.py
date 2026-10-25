import idle
"""exitsurvey.py OUT MACHINE K1,K2,.. T RTOP RDEF [MAXS]: start MACHINE at the exit Top(K) CL moment '0*2 7 1*K' (b = 366,
t = T; the Top clear gets R = RTOP, every later CL gets RDEF), run to the halt with the counter skip.  Per run: outcome,
ones, CL count, the bad H/I events (H0 with 0 on its left, H0 with left 1 but 0 two cells right, I0) AFTER the first
far-left event, the cascade exhaustion starts L = 3K-5 read off the stop CLs, the key (first orbit value < 60 of the
sub-step map) and a compact CL list."""
import sys, subprocess, re
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_h003check\hsim.exe'
MACH = {'h003': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0LI---_1RI1RC',
        'M8': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG---'}
def g(L):  # M8 sub-step map (C04 REPORT 2.3); None = stop
    r = L % 5
    return {1: (3 * L + 32) // 5, 2: (3 * L - 46) // 5, 3: (3 * L - 64) // 5, 4: (3 * L - 52) // 5}.get(r)
def key_of(L):
    while L >= 60:
        n = g(L)
        if n is None: L = (3 * L - 100) // 5; continue
        L = n
    return L
def run(m, K, T, RTOP, RDEF, MAXS='3e11', B=366):
    RL = [str(RTOP)] + str(RDEF).split(',')
    p = subprocess.run([EXE, MACH.get(m, m), '--kt', '0,0,7,1*%d;1;%d;%d' % (K - 1, 3 * B + 2, T), '--R', ','.join(RL),
                        '--Rdef', RL[-1], '--cnt', '--maxs', MAXS, '--ev', '400', '--view', '160'],
                       capture_output=True, text=True, creationflags=0x40)
    lines = p.stdout.splitlines()
    cls, bad, first, halt = [], [], None, None
    for l in lines:
        if l.startswith('CL'):
            k = int(re.search(r' K=(\d+)', l).group(1)); X = int(re.search(r' X=(\d+)', l).group(1))
            t = int(re.search(r' t=(\d+)', l).group(1)); v = l.split('|', 1)[1].strip()
            cls.append((X, k, t, v))
        elif l.startswith('  CNT'): cls.append(('CNT', l.strip(), 0, ''))
        elif l.startswith(('H0L0', 'H0ODD', 'I0')):
            if l.startswith('H0L0') and first is None: first = l; continue
            if first is not None and l.startswith('I0') and len(bad) == 0 and len(cls) <= 1: continue  # the first event's own I0 sweep
            bad.append(l[:160])
        elif l.startswith(('HALT', 'MAXS')): halt = l
    return cls, bad, halt, lines
if __name__ == '__main__':
    out = open(sys.argv[1], 'a'); m = sys.argv[2]
    Ks = [int(x) for x in sys.argv[3].split(',')]; T = int(sys.argv[4]); RTOP = int(sys.argv[5]); RDEF = sys.argv[6]
    MAXS = sys.argv[7] if len(sys.argv) > 7 else '3e11'
    for K in Ks:
        cls, bad, halt, lines = run(m, K, T, RTOP, RDEF, MAXS)
        starts = [3 * k - 5 for (X, k, t, v) in cls[1:] if X != 'CNT' and X == k + 7 and ' 0 2 z2 ' in ' ' + v + ' ']
        L0 = 3 * K - 2
        comp = ' '.join('%s/%s' % (X, k) if X != 'CNT' else 'CNT' for (X, k, t, v) in cls[1:])
        line = '%s K=%d K%%5=%d K%%25=%d T=%d RTOP=%d RDEF=%s | %s | bad=%d | ncl=%d L0=%d keyL0=%d starts=%s keys=%s | %s' % (
            m, K, K % 5, K % 25, T, RTOP, RDEF, (halt or 'NONE')[:90], len(bad), len(cls), L0, key_of(L0), starts[:12],
            [key_of(s) for s in starts][:12], comp[:600])
        print(line, flush=True); out.write(line + '\n')
        for b in bad[:6]: out.write('   BAD ' + b + '\n')
        out.flush()
