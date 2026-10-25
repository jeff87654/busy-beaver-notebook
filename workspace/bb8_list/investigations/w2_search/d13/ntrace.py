"""ntrace.py MACHINE MODE ARG STAGES SLOTS: follow (MODE=far: far_ARG + [0 1^41|1|19]; MODE=round: crafted round start
with c=ARG, z=415) and, for every stage that reads one of SLOTS, run n1/gtrace.exe to list those reads with context."""
import sys, threading, subprocess, os
from t1lib import stage, start_word, far_of, N1DIR
from nfol import run_stage
M, mode, arg, S, slots = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
GT = os.path.join(N1DIR, 'gtrace.exe')
QS = 'ABCDEFGHIJKLMNOP'
bits = [2 * QS.index(s[0]) + int(s[1]) for s in slots.split(',')]
def go():
    word = start_word([0] + [1] * 41 + [1, 19], far_of(arg)) if mode == 'far' else start_word([2, 5] + [1] * arg + [0, 0, 0, 3] + [1] * 415 + [1, 19])
    for st in range(S):
        out, u = run_stage(M, word, len(word), 'G', 4 * 10**8)
        if any(u >> b & 1 for b in bits):
            p = subprocess.run([GT, M, 'G', str(len(word)), str(4 * 10**8), slots, '14', '1'], input=word, capture_output=True, text=True)
            lines = [l for l in p.stdout.splitlines() if l.strip()]
            reads = [l for l in lines if ' | ' in l]
            print(f'stage {st}: {len(reads)} reads of {slots}')
            for l in reads[:4] + (['...'] + reads[-2:] if len(reads) > 6 else reads[4:]): print('   ', l[:110])
        kind, d = stage(M, word, 4 * 10**8)
        if kind != 'K': print('end', kind, d); return
        word = d[2]
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
