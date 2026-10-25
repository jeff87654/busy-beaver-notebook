# triage.py LIST OUT [BUDGET] : post-clear literal triage for template-RULED machines stuck after a CDP clear.
# For each machine: symsim --jumpdump gives the tape right after the first clear (X0 symbolic, residue known mod 38918880);
# substitute X0 := n for n = X0 mod 2520 (faithful mod 2520) and n+12 (faithful mod 12) and run the literal K-moment tracer.
# Evidence only (small-n substitution), never a proof.
import sys, re, subprocess, os
D = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(D)
lst, out = sys.argv[1], sys.argv[2]; bud = sys.argv[3] if len(sys.argv) > 3 else '1000000000'
tm = {l.split('\t')[0]: l.rstrip('\n').split('\t')[3] for l in open(os.path.join(B, 'kg', 'fitted.tsv'))}
done = set(l.split()[0] for l in open(out)) if os.path.exists(out) else set()
fo = open(out, 'a')
for m in [l.split()[0] for l in open(lst)]:
    if m in done: continue
    T = tm[m]; Q = T.split(',')[1]
    r = subprocess.run([os.path.join(B, 'symsim_v10b.exe'), 'run', '--tmpl', T, '--jumpstop', '--budget', '30000', '--tlimit', '30', '--sigwin', '0', '--mg', '38918880'],
                       input=f'{m} A\n', capture_output=True, text=True).stdout
    jt = [l for l in r.split('\n') if l.startswith('JUMPTAPE')]
    if not jt: fo.write(f'{m} NOJUMP\n'); fo.flush(); continue
    l = jt[0][9:]; tape, _, syms = l.partition('  ')
    ids = sorted(set(re.findall(r'X(\d+)=', syms)))
    if ids != ['0']: fo.write(f'{m} MULTISYM {syms.strip()}\n'); fo.flush(); continue
    res = int(re.search(r'\[r(\d+)\]', syms).group(1)); na = res % 2520
    for n in (na, na + 12):
        s = re.sub(r'\{([^}]*)\}', lambda g: str(eval(g.group(1).replace('X0', str(n)))), tape).split()
        cells = ''; head = None; q = 'A'
        for t in s:
            if len(t) == 2 and t[1] == '>': head = len(cells); q = t[0]; continue
            if len(t) == 2 and t[0] == '<': head = len(cells) - 1; q = t[1]; continue
            w, _, k = t.partition('^'); cells += w * (int(k) if k else 1)
        if head >= len(cells): cells += '0' * (head - len(cells) + 1)
        o = subprocess.run([os.path.join(D, 'kmom.exe'), m, Q, bud, '0', '-'], input=f'{cells} {head} {q}\n', capture_output=True, text=True).stdout.strip()
        fo.write(f'{m} n={n} {o[:500]}\n'); fo.flush()
