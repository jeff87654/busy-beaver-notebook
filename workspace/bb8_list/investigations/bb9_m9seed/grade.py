# grade.py: run machines (lines "machine start") at several representative bases, compare jump logs.
# usage: python grade.py infile outfile [budget] [R1,R2,R3]
import sys, subprocess, re
inf, outf = sys.argv[1], sys.argv[2]
budget = sys.argv[3] if len(sys.argv) > 3 else '20000000'
Rs = [int(x) for x in (sys.argv[4] if len(sys.argv) > 4 else '40,76,112').split(',')]
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_m9seed\m9s.exe'
ms = [l.split()[:2] for l in open(inf) if l.strip()]
def runlog(m, st, R):
    p = subprocess.run([EXE, 'run', budget, str(R), '100000', 'log'], input=f'{m} {st}\n', capture_output=True, text=True)
    jumps = []; leaf = None
    for l in p.stdout.splitlines():
        mm = re.match(r'\s+JUMP (\d+) step (\d+): Ch j=(\d+) b=(\d+) -> W=(\d+)( \(REP\))?', l)
        if mm: jumps.append((int(mm[3]), int(mm[4]), int(mm[5]), bool(mm[6])))
        if l.startswith('LEAF'): leaf = l.split()
    return leaf, jumps
with open(outf, 'w') as fo:
    for m, st in ms:
        res = [runlog(m, st, R) for R in Rs]
        outs = [r[0][3] for r in res]; nj = [len(r[1]) for r in res]; sig = [r[0][5] for r in res]
        # count jumps whose j scales with R (compare first two runs position-wise)
        a, b = res[0][1], res[1][1]
        scal = sum(1 for x, y in zip(a, b) if x[0] != y[0])
        nrep = [sum(1 for x in r[1] if x[3]) for r in res]
        cls = 'CONST' if len(set(nj)) == 1 else 'GROWS'
        fo.write(f'{m} {st} out={",".join(outs)} sigma={",".join(sig)} njumps={",".join(map(str,nj))} nrep={",".join(map(str,nrep))} jscaling={scal} {cls}\n')
        fo.write('   j-seq R1: ' + ' '.join(f'{x[0]}{"*" if x[3] else ""}' for x in a[:40]) + '\n')
        fo.write('   j-seq R2: ' + ' '.join(f'{x[0]}{"*" if x[3] else ""}' for x in b[:40]) + '\n')
        fo.flush()
