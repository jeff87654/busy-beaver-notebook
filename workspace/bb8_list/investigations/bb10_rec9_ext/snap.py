"""Snapshots of a run at given step counts: tape parsed into D-tokens (10)^m 1, junk as <...>, blocks compressed.
Usage: python snap.py MACHINE CONF n1,n2,...  [W]"""
import subprocess, sys, os, re
X = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xsim2.exe')
TMP = os.path.join(os.environ.get('CLAUDE_JOB_DIR', '.'), 'tmp', 'rec9ext')


def tokens(t, h):
    out, i = [], 0
    while i < len(t):
        if i == h:
            out.append('[H]')
        if t[i] == '1':
            j, k = i, 0
            while j + 2 < len(t) and t[j + 1] == '0' and t[j + 2] == '1' and not (j < h <= j + 2):
                j += 2; k += 1
            if j + 1 >= len(t) or t[j + 1] == '1':
                out.append(str(k)); i = j + 1; continue
            out.append('<' + t[i:j + 2] + '>' if j + 2 - i < 12 else f'<1(01)^{k}0>'); i = j + 2; continue
        z = i
        while i < len(t) and t[i] == '0' and i != h:
            i += 1
        if i == z:
            i += 1
        out.append(f'z{i - z}')
    return out


def rle(items, maxp=8):
    out, i = [], 0
    while i < len(items):
        best = (1, 1)
        for p in range(1, maxp + 1):
            r = 1
            while items[i + r * p:i + (r + 1) * p] == items[i:i + p] and i + (r + 1) * p <= len(items):
                r += 1
            if r > 1 and r * p > best[0] * best[1]:
                best = (r, p)
        r, p = best
        if r > 1:
            out.append(('(' if p > 1 else '') + ' '.join(items[i:i + p]) + (')' if p > 1 else '') + f'^{r}')
            i += r * p
        else:
            out.append(items[i]); i += 1
    return out


def main():
    m, conf, ns = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')]
    W = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    mf = os.path.join(TMP, 'snap_m.txt'); open(mf, 'w').write(m + chr(10))
    for n in ns:
        o = subprocess.run([X, mf, conf, str(n), '-d', '-p'], capture_output=True, text=True).stdout.split()
        tape = o[-1].split('=')[1]; h = int(o[-2].split('=')[1])
        toks = [x for x in tokens(tape, h)]
        print(n, o[1], 'state', o[3], 'pairs', o[-3].split('=')[1], '|', ' '.join(rle(toks))[:W], flush=True)


if __name__ == '__main__':
    main()
