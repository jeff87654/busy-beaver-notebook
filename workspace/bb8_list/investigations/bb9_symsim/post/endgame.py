# endgame.py LIST OUT [BUDGET] : counter-exhaustion test for post-clear machines (evidence only).
# After the first CDP clear (symsim --jumpdump, X0 := n = X0 mod 2520), trace literal K-moments, find the first K-moment whose tape is
# prefix (W)^k suffix with k >= 12n (the X0-sized block) and a short suffix (no other big run), then rerun from synthetic tapes with
# k := 0..4 and report HALT (sigma) / BUDGET / OVERFLOW for each.
import sys, re, subprocess, os
D = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(D)
lst, out = sys.argv[1], sys.argv[2]; bud = sys.argv[3] if len(sys.argv) > 3 else '3000000000'
tm = {l.split('\t')[0]: l.rstrip('\n').split('\t')[3] for l in open(os.path.join(B, 'kg', 'fitted.tsv'))}
done = set(l.split()[0] for l in open(out)) if os.path.exists(out) else set()
fo = open(out, 'a')
def expand(tokstr):
    out = ''; i = 0
    for m in re.finditer(r'\(([01]+)\)\^(\d+)\.|([01])', tokstr): out += m.group(1) * int(m.group(2)) if m.group(1) else m.group(3)
    return out
for m in [l.split()[0] for l in open(lst)]:
    if m in done: continue
    T = tm[m]; Q = T.split(',')[1]
    r = subprocess.run([os.path.join(B, 'symsim_v10b.exe'), 'run', '--tmpl', T, '--jumpstop', '--budget', '30000', '--tlimit', '30', '--sigwin', '0', '--mg', '38918880'],
                       input=f'{m} A\n', capture_output=True, text=True).stdout
    jt = [l for l in r.split('\n') if l.startswith('JUMPTAPE')]
    if not jt: fo.write(f'{m} NOJUMP\n'); fo.flush(); continue
    tape, _, syms = jt[0][9:].partition('  ')
    if sorted(set(re.findall(r'X(\d+)=', syms))) != ['0']: fo.write(f'{m} MULTISYM\n'); fo.flush(); continue
    n = int(re.search(r'\[r(\d+)\]', syms).group(1)) % 2520
    s = re.sub(r'\{([^}]*)\}', lambda g: str(eval(g.group(1).replace('X0', str(n)))), tape).split()
    cells = ''; head = None; q = 'A'
    for t in s:
        if len(t) == 2 and t[1] == '>': head = len(cells); q = t[0]; continue
        if len(t) == 2 and t[0] == '<': head = len(cells) - 1; q = t[1]; continue
        w, _, k = t.partition('^'); cells += w * (int(k) if k else 1)
    if head >= len(cells): cells += '0' * (head - len(cells) + 1)
    o = subprocess.run([os.path.join(D, 'kmom2.exe'), m, Q, '20000000', '1', 'x'], input=f'{cells} {head} {q}\n', capture_output=True, text=True).stdout.split('\n')
    found = None; cand = []
    for l in o:
        f = l.split()
        if len(f) < 5 or not f[1].startswith('km='): continue
        gap = int(f[3][4:]); ts = f[4]
        toks = list(re.finditer(r'\(([01]+)\)\^(\d+)\.', ts))
        big = [t for t in toks if int(t.group(2)) >= 12 * n]
        if len(big) != 1: continue
        b = big[0]
        if any(int(t.group(2)) > 30 for t in toks if t.start() > b.start()): continue
        cand.append((ts[:b.start()], b.group(1), int(b.group(2)), ts[b.end():], gap, f[0]))
    for i in range(len(cand) - 1):   # the LAST K-moment where an X0-sized block starts to decrease (counter use starts)
        if cand[i + 1][1] == cand[i][1] and cand[i][2] - 3 <= cand[i + 1][2] < cand[i][2] and (i == 0 or cand[i - 1][1] != cand[i][1] or cand[i - 1][2] < cand[i][2]):
            found = cand[i]
    if not found: fo.write(f'{m} n={n} NOBLOCK last={o[-2][:200] if len(o) > 1 else ""}\n'); fo.flush(); continue
    pre, W, k, suf, gap, st = found
    res = []
    for c in range(3):
        x = expand(pre) + W * c + expand(suf); hd = len(x) + gap
        r2 = subprocess.run([os.path.join(D, 'kmom2.exe'), m, Q, bud, '0', '-'], input=f'{x}{"0" * (gap + 1)} {hd} {Q}\n', capture_output=True, text=True).stdout.strip()
        res.append(f'c={c}:' + ' '.join(r2.split()[:4]))
    fo.write(f'{m} n={n} block=({W})^{k}@{st} pre={pre[:60]} suf={suf[:60]} gap={gap} | ' + ' | '.join(res) + '\n'); fo.flush()
