"""check_controls.py: run rank7 on the calibration controls and check the expected outcomes.
  positive: BB(7) champion (halts, level 13 +- 1), champ_231 (halts, level >= 19)
  negative: X33 and dl3's sibling i (never halt: invariant / round-2 'never halts')
Run after any change to rank7.py:  python check_controls.py"""
import idle  # noqa: F401
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONTROLS = [
    ('1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF', 'CHAMPION',
     'R,B,P=11,u=10,s=1,d=3d+1,b=3b+2,S=111001',
     'R1 2b+2 | R2 a=2b+2 b=0 | R3 2b+2+0k tail=0 a=0 b=0 | R4 HHHHH | H -', 'halt', 12.0, 14.0),
    ('1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB', 'CHAMPION',
     'L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1',
     'R1 1b+3 | R2 a=1b+3 b=0 | R3 1b+3-1k tail=1 a=1 b=0 | R4 HHHHH | H -', 'halt', 19.0, 99.0),
    ('1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE', 'R4-SOME',
     'R,A,P=110,u=1,s=0,d=1d+0,b=1b+0,S=-',
     'R1 1b+3 | R2 a=1b+2 b=1 | R3 1b+0+0k tail=1 a=2 b=1 | R4 HKHKH | H -', 'never', None, None),
    ('1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA0LG_---0LE', 'R4-SOME',
     'R,B,P=110,u=1,s=0,d=1d+0,b=3b+1,S=-',
     'R1 1b+1 | R2 a=3b+3 b=0 | R3 3b+1+0k tail=1 a=2 b=0 | R4 HKHTT | H -', 'never', None, None),
]


def main():
    fn = os.path.join(HERE, 'controls_in.tsv')
    with open(fn, 'w', newline='\n') as f:
        for m, g, t, p, *_ in CONTROLS:
            f.write('%s\t-1\t0\t%s\t%s\t%s\n' % (m, g, t, p))
    out = os.path.join(HERE, 'controls_out.tsv')
    subprocess.run([sys.executable, os.path.join(HERE, 'rank7.py'), fn, '-o', out, '--steps', '30000000'], check=True)
    rows = [ln.rstrip('\n').split('\t') for ln in open(out, encoding='utf-8')]
    H = rows[0]
    ix = {c: i for i, c in enumerate(H)}
    ok_all = True
    for m, g, t, p, want, lo, hi in CONTROLS:
        r = [x for x in rows[1:] if x[ix['machine']] == m][0]
        v, lv, nt, r2 = r[ix['verdict']], r[ix['est_level']], r[ix['notes']], r[ix['round2']]
        if want == 'halt':
            ok = v.split('+')[0] in ('RECORD?', 'CLOSE') and lo <= float(lv) <= hi
        else:
            ok = v.startswith('NEVER-HALTS') or 'never halts' in r2
        ok_all &= ok
        print('%-4s %s want %-5s got %s level %s | %s' % ('OK' if ok else 'FAIL', m, want, v, lv, (r2 if r2 != '-' else nt)[:90]))
    print('ALL CONTROLS OK' if ok_all else 'CONTROL FAILURE')
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
