"""Fast digit-list (Ackermann-style) scan: dlscan.exe screens, kfit.py confirms, and the halting boundary is graded.

  python dlscan.py machines.txt out.tsv [--steps 5000000] [--N 100000]

This replaces `stage1.exe` + `scan_ack.py` + `ack_general.py` (about 10 s per machine) at about 0.05 s per machine:
1. `dlscan.exe` (dlscan.cpp) runs the census at both tape ends and the R1/R2/R3 probes in C++. It returns the
   keys (orientation, state, suffix, unit, sep) whose probes look like a digit-list counter ("full"), and those
   that only count down and reset one digit ("partial": R1 and R2 but not R3).
2. Every full key is confirmed with the unchanged `kfit.py` (1,000,000-step probes). A machine with a key whose
   R1, R2 and R3 all fit is a DIGIT-LIST machine, as in scan_ack.py. Keys with orientation L are fitted on the
   mirror image of the machine (L and R swapped), which behaves identically with the tape reversed.
3. Each confirmed key gets a halting grade from kfit's safety conditions (the parent's non-halting argument):
     SAFE        s1-s5 hold: the parent's shape (resets leave a = b = 1), resets keep b >= k+1 and the halting
                 boundary is above that, so the parent's non-halting argument applies
     HALT?       s4 fails: the halting boundary k = mh*b + ch is not above the b-1 trailing zeros a reset can meet
     CHECK       s1, s2, s3 or s5 fails: the rules fit, but the parent's invariant does not carry over as is
     NOBOUNDARY  no halting boundary was found (R3 never halts in the probed range)
     HALT-SOME   no linear boundary, but some reset probes halt (e.g. only for some b)
     R4-SOME     the empty list (R4) halts for some b: the BB(9) champion's pattern (it halts for odd b)
   The machine's grade is the safest grade among its confirmed keys, since one SAFE description is enough.
   HALT?, R4-SOME, HALT-SOME and CHECK machines are the ones worth an investigation: a digit-list counter
   that might halt.

out.tsv: machine, verdict (DIGIT-LIST / unconfirmed / partial), grade, details.
"""
import ast
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent / 'investigations' / 'neighbors_family_tools'
EXE = HERE / 'dlscan.exe'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
GRADES = ['SAFE', 'NOBOUNDARY', 'CHECK', 'HALT-SOME', 'R4-SOME', 'HALT?']   # safest first


def mirror(tm):
    return tm.translate(str.maketrans('LR', 'RL'))


def screen(src, out, steps=5000000, N=100000):
    """Run dlscan.exe. Return (rows, summary): rows = [(machine, [full keys], [partial keys])]."""
    subprocess.run([str(EXE), str(src), str(out), str(steps), str(N)], check=True, creationflags=LOW)
    return read_screen(out)


def read_screen(out):
    rows, summary = [], None
    for l in Path(out).read_text().splitlines()[1:]:
        f = l.split('\t')
        if f[0] == '#summary':
            summary = dict(x.split('=') for x in f[1:])
        else:
            rows.append((f[0], [] if f[3] == '-' else f[3].split(';'), [] if f[4] == '-' else f[4].split(';')))
    return rows, summary


def grade(safety):
    if safety is None:
        return 'NOBOUNDARY'
    if not safety['s4']:
        return 'HALT?'
    if not (safety['s1'] and safety['s2'] and safety['s3'] and safety['s5']):
        return 'CHECK'
    return 'SAFE'


def confirm(tm, key, N=10 ** 6):
    """kfit.py on one key. Return (rules line, grade) if R1, R2 and R3 fit, else None."""
    o, q, suf, u, sep = key.split(',')
    env = dict(os.environ, BB_KENC=f'{u},{sep}')
    try:
        r = subprocess.run([sys.executable, str(TOOLS / 'kfit.py'), mirror(tm) if o == 'L' else tm,
                            '--shape', f'{q},{suf}', '--N', str(N)],
                           cwd=TOOLS, capture_output=True, text=True, timeout=300, env=env, creationflags=LOW)
    except subprocess.TimeoutExpired:
        return None
    lines = [l.strip() for l in r.stdout.splitlines()]
    rules = next((l for l in lines if l.startswith('R1:')), '')
    parts = [p.strip() for p in rules.split('|')]
    ok = lambda tag: any(p.startswith(tag) and 'no fit' not in p for p in parts)
    if not (ok('R1:') and ok('R2:') and ok('R3:')):
        return None
    saf = next((l for l in lines if l.startswith('safety:')), 'safety: None')
    g = grade(ast.literal_eval(saf[len('safety:'):].strip()))
    if g == 'NOBOUNDARY':
        # No linear halting boundary, but some probes may still halt: a halt that depends on b (for instance
        # on its parity, as in the BB(9) champion, which halts on an empty list for odd b only) must not be
        # filed as harmless.
        kh = next((l for l in lines if l.startswith('kh:')), 'kh: {}')
        r4 = next((l for l in lines if l.startswith('R4 raw:')), '')
        if 'HALT' in r4:
            g = 'R4-SOME'
        elif any(k < b for b, k in ast.literal_eval(kh[len('kh:'):].strip()).items()):
            # only halts at k < b matter: a reset with k >= b trailing zeros is outside the rule's range and,
            # in every machine proved so far (884431, 048631, 240161), unreachable (b > k at every reset)
            g = 'HALT-SOME'
    return rules, g


def judge(tm, full, partial):
    """Return (verdict, grade, details) for one screened machine."""
    hits = []
    for key in full:
        c = confirm(tm, key)
        if c:
            hits.append((key, c[0], c[1]))
            if c[1] == 'SAFE':      # the safest grade: no other key can change the machine's grade
                break
    if hits:
        g = min((h[2] for h in hits), key=GRADES.index)
        return 'DIGIT-LIST', g, ' || '.join(f'{k} [{gr}]: {rules}' for k, rules, gr in hits)
    if full:
        return 'unconfirmed', '-', ';'.join(full)
    return 'partial', '-', ';'.join(partial)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    opt = lambda name, d: int(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else d
    for name in ('--steps', '--N'):
        if name in sys.argv:
            args.remove(sys.argv[sys.argv.index(name) + 1])
    src, out = Path(args[0]), Path(args[1])
    rows, summary = screen(src, out.with_suffix('.screen.tsv'), opt('--steps', 5000000), opt('--N', 100000))
    n = {'DIGIT-LIST': 0, 'unconfirmed': 0, 'partial': 0}
    with open(out, 'w', newline='\n') as f:
        f.write('machine\tverdict\tgrade\tdetails\n')
        for tm, full, partial in rows:
            verdict, g, details = judge(tm, full, partial)
            n[verdict] += 1
            f.write(f'{tm}\t{verdict}\t{g}\t{details}\n')
            if verdict == 'DIGIT-LIST':
                print(f'DIGIT-LIST [{g}] {tm}   {details[:160]}', flush=True)
    print(f"scanned {summary['machines']} machines: {n['DIGIT-LIST']} digit-list, {n['unconfirmed']} unconfirmed "
          f"screen hits, {n['partial']} partial (R1+R2 only)", flush=True)


if __name__ == '__main__':
    main()
