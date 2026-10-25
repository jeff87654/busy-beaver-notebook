"""Probe 0LA+J children that ran out of time/space right after the redirect: run from 0LA's stage-2 configuration
[D9^3, D8, D0, 0^k | 0 | r] with a growing step budget and report the tape extent and the result."""
import sys, mf35
rows = [l.split('\t') for l in open('ola_j.tsv')]
for f in rows:
    if f[1] not in ('TIME', 'WIDE'):
        continue
    m = f[0]
    out = []
    for k, r in ((20, 19), (67, 19)):
        toks = [9] * 3 + [8, 0] + [1] * k + [1, r, 2]
        w = mf35.word_of_tokens(toks)
        ext = []
        for ms in (10**5, 10**6, 10**7):
            sv = mf35._server()
            sv.stdin.write(f'{m} G {len(w)} {ms} 10000000 600\n{w}\n'); sv.stdin.flush()
            o = sv.stdout.readline().strip()
            ext.append(o.split()[0] + o.split()[1][:9])
            if o[0] != 'T':
                break
        out.append(f'k={k}:' + ','.join(ext))
    print(m[56:], f[1], ' '.join(out), flush=True)
