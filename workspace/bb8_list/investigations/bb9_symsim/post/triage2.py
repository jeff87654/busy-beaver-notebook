# triage2.py LIST OUT [BUDGET TLIMIT ROUNDS] : chained n-substituted symbolic continuation after CDP clears (evidence only).
# Round 0: symsim --jumpstop gives the tape right after the first clear.  Each round: substitute every symbol X by n = (residue of X
# mod 38918880) mod 2520 (faithful mod 2520; real values are huge), continue with symsim --tmpl --jumpdump from that exact tape;
# if it ends BUDGET after a further clear, the next round starts from the last post-clear tape.  Records the per-round verdicts.
import sys, re, subprocess, os
D = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(D)
lst, out = sys.argv[1], sys.argv[2]; bud = sys.argv[3] if len(sys.argv) > 3 else '300000'; tl = sys.argv[4] if len(sys.argv) > 4 else '120'
rounds = int(sys.argv[5]) if len(sys.argv) > 5 else 4
tm = {l.split('\t')[0]: l.rstrip('\n').split('\t')[3] for l in open(os.path.join(B, 'kg', 'fitted.tsv'))}
done = set(l.split()[0] for l in open(out)) if os.path.exists(out) else set()
fo = open(out, 'a')
EXE = os.path.join(B, 'symsim_v12.exe')
def subst(tape, syms):
    res = {k: int(v) % 2520 for k, v in re.findall(r'X(\d+)=[^\[]*\[r(\d+)\]', syms)}
    def ev(g):
        e = g.group(1)
        for k in sorted(res, key=lambda z: -len(z)): e = re.sub(r'X' + k + r'(?!\d)', str(res[k]), e)
        if 'X' in e: raise ValueError('unresolved ' + e)
        return str(eval(e.replace('/', '//')))
    return re.sub(r'\{([^}]*)\}', ev, tape), res
for m in [l.split()[0] for l in open(lst)]:
    if m in done: continue
    T = tm[m]
    r = subprocess.run([EXE, 'run', '--tmpl', T, '--jumpstop', '--budget', '100000', '--tlimit', '60', '--sigwin', '0', '--mg', '38918880', '--memcap', '1500'],
                       input=f'{m} A\n', capture_output=True, text=True).stdout
    jt = [l for l in r.split('\n') if l.startswith('JUMPTAPE')]
    if not jt: fo.write(f'{m} NOJUMP\n'); fo.flush(); continue
    log = []; cur = jt[0][9:]
    for rd in range(rounds):
        tape, _, syms = cur.partition('  ')
        try: s, res = subst(tape, syms)
        except Exception as e: log.append(f'R{rd}:SUBSTFAIL'); break
        o = subprocess.run([EXE, 'run', '--tmpl', T, '--jumpdump', '--budget', bud, '--tlimit', tl, '--sigwin', '0', '--mg', '38918880', '--memcap', '1500'],
                           input=f'{m} A {s}\n', capture_output=True, text=True)
        R = [l for l in o.stdout.split('\n') if l.startswith('R ')]
        J = [l for l in o.stdout.split('\n') if l.startswith('JUMPTAPE')]
        alt = ','.join(sorted(set(l.split()[1] + ':' + l.split()[3] for l in o.stderr.split('\n') if l.startswith('KGALT'))))
        if not R: log.append(f'R{rd}:NOR'); break
        f = R[0].split(); v = f[3]; kj = [x for x in f if x.startswith('kj=')][0]; sg = [x for x in f if x.startswith('sigma=')][0]
        jl = R[0].split('|')[1].strip() if '|' in R[0] else ''
        log.append(f'R{rd}:{v} {kj} {sg} [{jl}]' + (f' alt={alt}' if alt else ''))
        if v != 'BUDGET' or not J: break
        cur = J[-1][9:]
    fo.write(f'{m} | ' + ' || '.join(log) + '\n'); fo.flush()
