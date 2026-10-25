"""ehalt.py REPS OUT KMAX BMAX STEPS: for each machine, exhaustion probes E(k;b)=K(0^k;0;b) (out.tsv template),
k=0..KMAX, b=0..BMAX; record which (k,b) halt within STEPS. Output: machine, then per k the halting b values."""
import idle, sys, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
reps, out, KM, BM, ST = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(float(sys.argv[5]))
with open(out, 'a') as fo:
    for M in open(reps).read().split():
        T = kl.tmpl(M); res = []
        for k in range(KM + 1):
            hb = []
            for b in range(BM + 1):
                w = kl.word(T, [0] * k, 0, b)
                p = subprocess.run([kl.EXE, M] + kl.args(T) + [str(ST), '1000000000', '0', w, str(len(w)), T['q'], '0'],
                                   capture_output=True, text=True, creationflags=0x40)
                if 'HALT' in p.stdout: hb.append(b)
            res.append(f'k={k}:' + ','.join(map(str, hb)))
        fo.write(M + '\t' + ' '.join(res) + '\n'); fo.flush()
