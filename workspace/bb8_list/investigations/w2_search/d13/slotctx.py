"""slotctx.py MACHINE MODE ARG STAGES SLOTS [WIN] [--from S]: like ntrace.py but prints EVERY read of SLOTS (with context)
per stage, plus a per-stage slot histogram.  MODE=far: far_ARG + [0 1^N|1|19] (N env, default 41);
MODE=round: crafted round start [2 5 1^ARG 0^3 3 1^Z|1|19] (Z env, default 415)."""
import sys, threading, subprocess, os
from t1lib import stage, start_word, far_of, N1DIR
from nfol import run_stage
M, mode, arg, S, slots = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
WIN = sys.argv[6] if len(sys.argv) > 6 and not sys.argv[6].startswith('--') else '14'
FROM = int(sys.argv[sys.argv.index('--from') + 1]) if '--from' in sys.argv else 0
N = int(os.environ.get('N', 41)); Z = int(os.environ.get('Z', 415)); POL = os.environ.get('POL', 'std')
R0 = 2539 if POL == 'big' else 19
GT = os.path.join(N1DIR, 'gtrace.exe')
QS = 'ABCDEFGHIJKLMNOP'
bits = [2 * QS.index(s[0]) + int(s[1]) for s in slots.split(',')]
def go():
    word = start_word([0] + [1] * N + [1, R0], far_of(arg)) if mode == 'far' else start_word([2, 5] + [1] * arg + [0, 0, 0, 3] + [1] * Z + [1, R0])
    for st in range(S):
        if st >= FROM:
            out, u = run_stage(M, word, len(word), 'G', 4 * 10**9)
            if any(u >> b & 1 for b in bits):
                p = subprocess.run([GT, M, 'G', str(len(word)), str(4 * 10**9), slots, WIN, '1'], input=word, capture_output=True, text=True)
                reads = [l for l in p.stdout.splitlines() if ' | ' in l]
                h = {}
                for l in reads:
                    s_ = l.split()[1]; h[s_] = h.get(s_, 0) + 1
                print(f'stage {st}: {len(reads)} reads', h, flush=True)
                for l in reads: print('   ', l[:140])
        kind, d = stage(M, word, 4 * 10**9, POL)
        if kind != 'K': print('end', kind, d); return
        if st >= FROM: print(f'  -> K st={st} far={len(d[1])}b toks={" ".join(map(str, d[0][:12]))}{" ..." if len(d[0]) > 12 else ""} ev={d[3]}', flush=True)
        word = d[2]
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
