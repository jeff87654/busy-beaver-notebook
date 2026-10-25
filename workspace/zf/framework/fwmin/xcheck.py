"""TM-vs-RM crosscheck (logic of zf/tools/crosscheck.py, made importable) + first-N dispatch tape comparison
against Wade's zf2.tm.  Usage: python -I xcheck.py FILE.tm MAXSTEPS [NTAPES]"""
import sys, re, importlib.util
TOOLS = r'C:\Users\jeffr\Downloads\bb8\zf\tools'
sys.path.insert(0, TOOLS)
from tmsim import load
from dag import extract, RM, walk
ZF2TM = r'C:\Users\jeffr\Downloads\bb8\zf\ext\turing_machine_explorer\zf2.tm'

def crosscheck(path, maxsteps, verbose=True, init=None):
    start, tbl, nodes, regidx = extract(path)
    nreg = len(regidx); rm = RM(nodes, 'main().0', nreg)
    tape = {}; pos = 0; st = start; steps = 0
    if init is not None:   # synthetic post-boot dispatch tape: (gap g, number of zero registers n)
        g, n = init; st = 'main().0'; tape = {-1: '1'}
        for i in range(n): tape[g + 2 * i] = '1'
    nops = 0; minmargin = 10**9; mismatch = 0; mingap = 10**9
    while steps < maxsteps and not rm.halted:
        if st == 'main().0':
            hi = max(tape)
            ip = ''.join(tape.get(i, '0') for i in range(pos, hi + 1))
            allbits = [int(c) for c in ip] + [0] * 400
            leaf, d = walk(nodes, 'main().0', allbits)
            ones = 0
            while allbits[d + ones] == 1: ones += 1
            gap = 0
            while d + ones + gap < len(ip) and allbits[d + ones + gap] == 0: gap += 1
            mingap = min(mingap, gap)
            bits = allbits[:d + ones]; rf = ip[d + ones:]
            if ones == 0:
                runs = re.split(r'0+', rf.strip('0'))
                regs_tm = [len(r) - 1 for r in runs if r][-nreg:][::-1]
                if (rm.P + [0] * 300)[:300] != (bits + [0] * 300)[:300] or regs_tm != rm.regs:
                    mismatch += 1
                    if verbose: print('MISMATCH step', steps, 'op', nops, bits, regs_tm, rm.P, rm.regs)
                    if mismatch > 5: break
                rm.step(regidx); nops += 1
            need = (regidx[leaf[1]] + 1 if leaf[0] == 'op' else 0) + 3
            minmargin = min(minmargin, (ones + gap) - need)
        t = tbl.get((st, tape.get(pos, '0')))
        if t is None: break
        w, dd, n = t; tape[pos] = w; pos += 1 if dd == 'R' else -1; st = n; steps += 1
    return dict(steps=steps, ops=nops, mismatches=mismatch, min_margin=minmargin, min_gap=mingap,
                regs=rm.regs, halted=rm.halted)

def dispatch_tapes(path, n, maxsteps=10**7):
    start, tbl = load(path)
    tape = {}; pos = 0; st = start; steps = 0; out = []
    while steps < maxsteps and len(out) < n:
        if st == 'main().0':
            lo = min(tape); hi = max(tape)
            out.append((''.join(tape.get(i, '0') for i in range(lo, pos)).lstrip('0'),
                        ''.join(tape.get(i, '0') for i in range(pos, hi + 1)).rstrip('0')))
        t = tbl.get((st, tape.get(pos, '0')))
        if t is None: break
        w, d, nx = t; tape[pos] = w; pos += 1 if d == 'R' else -1; st = nx; steps += 1
    return out

def decode(t, nreg=11):
    """(left, right) -> (P string up to the gap, gap length, register values right-to-left, number of runs)"""
    left, right = t
    m = re.match(r'([01]*?)(0*)((?:1+0)*1+)$', right)
    ipj, gap, rf = m.group(1), m.group(2), m.group(3)
    runs = rf.split('0')
    return ipj, len(gap), [len(r) - 1 for r in runs][-nreg:][::-1], len(runs)

def compare_tapes(path, n=30):
    a = dispatch_tapes(ZF2TM, n); b = dispatch_tapes(path, n)
    exact = sum(1 for x, y in zip(a, b) if x == y)
    dec = sum(1 for x, y in zip(a, b) if decode(x)[0] == decode(y)[0] and decode(x)[2] == decode(y)[2])
    gaps = [(decode(x)[1], decode(y)[1]) for x, y in zip(a, b)]
    return dict(n=min(len(a), len(b)), exact=exact, same_IP_and_regs=dec, gap_delta=sorted({gy - gx for gx, gy in gaps}))

if __name__ == '__main__':
    p = sys.argv[1]; ms = int(sys.argv[2]); nt = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    print('crosscheck', crosscheck(p, ms))
    print('dispatch tapes vs zf2.tm', compare_tapes(p, nt))
