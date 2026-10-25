"""Probe the literal stages of the period of M3 = 1RB0RA_..._1LI0LC_..._---0LJ_0LD0RA on constructed inputs.
Prints the next jump K-moment (tokens far-first, compressed) for each input.  python m3probe.py S2|S3|S4"""
import sys
import mf35
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA'


def nextj(toks, maxs=200_000_000, raw=False):
    w = mf35.word_of_tokens(toks)
    sv = mf35._server()
    sv.stdin.write(f'{M} G {len(w)} {maxs} 4000000 600\n{w}\n')
    sv.stdin.flush()
    o = sv.stdout.readline().strip().rpartition(' | U=')[0]
    if not o.startswith('J'):
        return o
    t = [int(x) for x in o.split('|')[1].split()][::-1]
    far = o.split('|')[2].strip()
    if raw:
        return t, far
    return ('<far>' if far else '') + mf35.rle(t)


F = [6] * 3
if __name__ == '__main__':
    kind = sys.argv[1]
    for C in (12, 20, 33):
        for x in (2 * 7 + 3, 2 * 19 + 3, 2 * 31 + 3):            # x = 2r+3 (unpacked token)
            for R in (7, 19, 43):                               # current accumulator token
                for Z in (10, 37):
                    if kind == 'S2':
                        toks = F + [3, C, x, 0] + [1] * Z + [1, R, 2]
                    elif kind == 'S3':
                        toks = F + [3, C, 2, 0, 2] + [1] * Z + [1, R, 2]
                    else:
                        toks = F + [3, C, 2] + [1] * Z + [1, R, 2]
                    print(kind, f'C={C} x={x} R={R} Z={Z} ->', nextj(toks), flush=True)
