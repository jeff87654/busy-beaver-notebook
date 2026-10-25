"""Check the transcription: the record run from d2start(q, b) halts exactly at c_end(q, 3b-3) (tape and head)."""
import subprocess, sys, os
from cend import c_end, d2start, PAD
REC = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---'
TMP = os.path.join(os.environ.get('CLAUDE_JOB_DIR', '.'), 'tmp', 'rec9ext')
os.makedirs(TMP, exist_ok=True)

def write_conf(cfg, fn):
    tape, head, st = cfg
    open(fn, 'w').write(f'{st} {head}\n{tape}\n')

def trim(tape, head):
    a = min(tape.index('1'), head); b = max(tape.rindex('1'), head)
    return tape[a:b + 1], head - a

ok = True
mf = os.path.join(TMP, 'rec.txt'); open(mf, 'w').write(REC + '\n')
for q in range(0, 6):
    for b in range(2, 7):
        cf = os.path.join(TMP, 'd2.txt'); write_conf(d2start(q, b), cf)
        out = subprocess.run(['./xsim.exe', mf, cf, '2000000000', '-d'], capture_output=True, text=True).stdout.split()
        kind, steps = out[1], int(out[2])
        tape = out[-1].split('=')[1]; ho = int(out[-2].split('=')[1])
        ct, ch, cs = c_end(q, 3 * b - 3)
        exp = trim(ct, ch)
        good = kind == 'H' and out[3] == 'I' and out[4] == '1' and (tape, ho) == exp
        ok &= good
        print(q, b, kind, steps, out[3], out[4], 'MATCH' if good else 'MISMATCH')
print('ALL MATCH' if ok else 'SOME MISMATCH')
