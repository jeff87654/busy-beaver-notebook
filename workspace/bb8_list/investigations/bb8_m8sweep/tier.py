"""tier.py IN_DIR OUT_DIR LEVEL SHARD NSHARD : rerun promoted leaves of a screen directory with a larger budget.

LEVEL 2: promote leaves (from IN_DIR/<i>_<X>_c<c>_<v>.txt, tier-1 files) that did not halt and have esc_after >= 1,
         budget --maxt 3e8; stop at esc_after >= 6 (ESCMAX).
LEVEL 3: promote tier-2 results (IN_DIR = tier-2 dir) with esc_after >= 2 that did not halt, budget 6e9.
Halting leaves are never rerun (their outcome is final). The base world settings are read from IN_DIR/<i>.json.
Output: OUT_DIR/<group>.txt (one wf line per leaf, same format), resumable per group.
"""
import sys, os, json, time, subprocess, glob, re
HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(HERE, 'wf8.exe')
IDLE = 0x40
BUD = {2: ('3e8', 6), 3: ('2.5e9', 8)}


def run(cmd, out):
    with open(out + '.tmp', 'w') as fo:
        p = subprocess.Popen(cmd, stdout=fo, stderr=subprocess.STDOUT, creationflags=IDLE | 0x08000000, cwd=HERE)
        with open(os.path.join(HERE, 'pids.txt'), 'a') as pf:
            pf.write('%d\t%s\t%s\n' % (p.pid, time.strftime('%Y-%m-%d %H:%M:%S'), ' '.join(cmd)[:200]))
        p.wait()
    os.replace(out + '.tmp', out)


def esc_of(l):
    m = re.search(r' esc=(\d+)', l)
    return int(m.group(1)) if m else -1


def main():
    ind, outd, lev, sh, ns = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    scrdir = sys.argv[6] if len(sys.argv) > 6 else ind      # where the base summaries / snapshots live
    os.makedirs(outd, exist_ok=True)
    maxt, escadd = BUD[lev]
    summ = {}
    for f in glob.glob(os.path.join(scrdir, '[0-9][0-9][0-9].json')):
        o = json.load(open(f))
        if 'runs' in o:
            summ[o['i']] = o
    groups = {}
    for i, o in sorted(summ.items()):
        for r in o['runs']:
            if 'file' not in r:
                continue
            g = r['file'][:-4]
            src = os.path.join(ind, r['file'])
            if not os.path.exists(src):
                continue
            e0 = r['snap']['nesc']
            sel = []
            for l in open(src):
                f = l.split()
                if len(f) < 2 or f[1] in ('HALT', 'SNAPPED', 'LOOP') or f[0].startswith('#'):
                    continue
                ea = esc_of(l) - e0
                if (lev == 2 and ea >= 1) or (lev == 3 and ea >= 2):
                    sel.append(f[0])
            if sel:
                groups[g] = (i, r, sel, e0)
    keys = sorted(groups)
    for n, g in enumerate(keys):
        if n % ns != sh:
            continue
        outf = os.path.join(outd, g + '.txt')
        if os.path.exists(outf):
            continue
        i, r, sel, e0 = groups[g]
        o = summ[i]
        c = r['c']; M = o['M']
        r0 = c if c >= 4 else c + M
        common = ['--rc', '10', '--rk', '1', '--cls', str(c), str(M), '--R0', str(r0)]
        if o['tmpl'].startswith('R,B,P=11,u=10,s=1,d=3d+1,b=3b+2'):
            common += ['--tail', '11/11111100/1001']
        snapf = os.path.join(scrdir, '%03d_%s_c%d_snap.txt' % (i, r['X'], c))
        lst = os.path.join(outd, g + '.list')
        open(lst, 'w').write('\n'.join(sel) + '\n')
        run([WF, '--batch', lst, o['tmpl']] + common + ['--x', r['X'], '--from', snapf, '--maxt', maxt, '--maxs', maxt,
                                                      '--escmax', str(e0 + escadd), '--loop', '--slit', '3e6', '--maxexact', '3e7', '--xmax', '200000'], outf)


if __name__ == '__main__':
    main()
