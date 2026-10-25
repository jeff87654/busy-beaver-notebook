"""halts_exact.py: exact halting step and ones for halts.tsv rows (ms.exe at the row's K), -> halts_exact.tsv"""
import idle  # noqa
import subprocess
MS = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
out = open('halts_exact.tsv', 'w'); out.write('machine\tK\tsteps\tones\n')
for l in open('halts.tsv'):
    f = l.split('\t'); m, K = f[0], f[1]
    r = subprocess.run([MS, m, K, '20000000', 'p0'], capture_output=True, text=True).stdout.strip().splitlines()
    last = r[-1] if r else ''
    if last.startswith('H '):
        d = dict(x.split('=') for x in last.split()[1:])
        out.write(f"{m}\t{K}\t{float(d['steps']):.0f}\t{float(d['ones']):.0f}\n")
    else:
        out.write(f"{m}\t{K}\t?\t{last}\n")
out.close()
