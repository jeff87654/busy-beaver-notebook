"""Stage 0 of the 1LD1LC machine on a b-grid: from the GH base machine's E0 configuration after K(0^35; 0; b)
(built literally by e0cfg.exe from the K word 1 (011)^36 (01)^(3b+1) 1010, state G) run the full machine to its first
non-small K-moment; expect [9^u 11 1^(m+1) | 1 | 2] with u = (12b+8)/5, m = 2u+35.  Requires b == 1 (mod 5).
usage: python stage0.py b1 b2 ...   (or 'grid' for b = 1, 6, ..., 196)"""
import sys, subprocess, time
sys.path.insert(0, r"C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/v1LD1LC")
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import mf35g
from lit1 import M, FAM, F, rle, fmt
HERE = r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/v1LD1LC'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)

def e0cfg(b):
    w = '1' + '011' * 36 + '01' * (3 * b + 1) + '1010'
    out = subprocess.run([HERE + '/e0cfg.exe', F['base'], w, str(len(w)), 'G', str(10 ** 12)], capture_output=True, text=True,
                         creationflags=LOW).stdout.strip()
    f = out.split()
    if f[0] != 'E' or f[2] != 'E' or f[3] != '0':
        raise RuntimeError(f'base machine did not stop at E0: {out[:100]}')
    head = int(f[4]); word = out.split('| ')[1].strip()
    return word, head, int(f[1])

def stage0(b, maxs=10 ** 11):
    word, head, bstep = e0cfg(b)
    out = mf35g.run_stage(FAM, M, word, head, 'E', maxs)
    f = out.split()
    if f[0] != 'J':
        return False, out[:120], bstep
    parts = out.split('|'); toks = [int(x) for x in parts[1].split()]
    far = parts[2].strip() if len(parts) > 2 else ''
    toks = toks[::-1]           # farthest-first incl. a, r at the end
    u = (12 * b + 8) // 5; m = 2 * u + 35
    exp = [9] * u + [11] + [1] * (m + 1) + [1, 2]
    return (toks == exp and not far), f'K: {rle(toks[:-2])} | a={toks[-2]} r={toks[-1]} step={f[1]}' + (' FAR' if far else ''), bstep

if __name__ == '__main__':
    bs = list(range(1, 197, 5)) if sys.argv[1] == 'grid' else [int(x) for x in sys.argv[1:]]
    bad = 0
    for b in bs:
        if b % 5 != 1:
            print(f'b={b} skipped (not 1 mod 5)'); continue
        t0 = time.time()
        ok, msg, bstep = stage0(b)
        bad += not ok
        print(f'b={b} {"ok" if ok else "FAIL"} base->E0 at step {bstep}; {msg[:160]} ({time.time()-t0:.0f}s)', flush=True)
    print(f'STAGE0 {len(bs)} values, {bad} mismatches')
