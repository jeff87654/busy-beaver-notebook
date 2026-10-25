"""ctl.py: positive control on the BB(7) champion. Step 1: from the champion's exhaustion configs K(0^n;0;b)
(word from bb8_resid/tools/exhcfg.py) is the halt slot E0 reached? Step 2/3: all 288 children (E0 -> xyH, H free with
>= 1 halt; + 28 same-state redirects) followed literally from the same configs: halt soon after the slot (no rebuild)
vs survive the budget."""
import subprocess, sys, os
D = os.path.dirname(os.path.abspath(__file__)); EXE = os.path.join(D, 'litk.exe')
CH = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF'
M8 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG---'
def word(n, b): return '11' + '101' * (n + 1) + '10' * (3 * b + 2) + '111001'
def run(m, w, mx):
    p = subprocess.Popen([EXE, m, w, '1', str(mx)], stdout=subprocess.PIPE, text=True, creationflags=0x40)
    open(os.path.join(D, '..', 'pids.txt'), 'a').write(f'{p.pid} litk control\n'); return p.communicate()[0].strip()
mode = sys.argv[1]
if mode == 'slot':
    for n in range(0, 9):
        row = []
        for b in range(0, 41):
            r = run(CH, word(n, b), 10**8); row.append('E0' if r.startswith('HALT') and ' E0 ' in r else r[:12])
        print(n, ' '.join(sorted(set(row))), flush=True)
else:
    ch = subprocess.run([sys.executable, os.path.join(D, '..', 'src', 'children.py'), CH, 'E0', '--same'], capture_output=True, text=True).stdout.split()
    cfgs = [(0, 0), (1, 0), (2, 1), (0, 2), (3, 3)]
    for m in ch:
        res = [run(m, word(n, b), int(sys.argv[2])) for n, b in cfgs]
        tag = 'SURVIVE' if all(r.startswith('END') for r in res) else ('HALT' if all(r.startswith('HALT') for r in res) else 'MIXED')
        print(tag, m, ' | '.join(x[:40] for x in res), '<-- M8' if m == M8 else '', flush=True)
