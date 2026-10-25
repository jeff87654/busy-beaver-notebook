"""nhrun.py: the 3 natural-run halters with 2 undefined slots (nonlist/halts.tsv, halt at ~1e10-1e11 steps).
For each undefined slot, all 28 completions (w d X, X in A..G); natural macro run (nlp7v, the K that saw the base halt,
3e6 macro steps). The slot whose completions do not change the base halt is not the first-reached one."""
import idle  # noqa
import subprocess, os
NL = os.path.abspath('../nonlist/nlp7v.exe')
bases = [('1RB---_1RC0LF_1RD---_0RE0LG_1LF0RG_1LG1LF_0LB0RB', 5), ('1RB0LA_1LC0RB_0RF1LD_0LE1LG_1LA0LB_---1RB_1LE---', 4),
         ('1RB0LD_1RC1RG_0RD1RA_0LE0RB_0RF1LA_1LG---_0LA---', 3)]
for i, (b, K) in enumerate(bases):
    ms = [b]
    for p in range(len(b)):
        if b[p:p+3] == '---' and (p % 7) in (0, 3):
            ms += [b[:p] + w + d + x + b[p+3:] for w in '01' for d in 'LR' for x in 'ABCDEFG']
    open(f'nh/in{i}.txt', 'w').write('\n'.join(ms) + '\n')
    p = subprocess.Popen([NL, f'nh/in{i}.txt', f'nh/out{i}.tsv', '3000000', '--life', f'--K={K}'])
    open('pids.txt', 'a').write(f'nhrun child={p.pid} base{i}\n'); p.wait()
