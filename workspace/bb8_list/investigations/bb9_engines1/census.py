"""census.py: for each base (machine, template) of a watch_hits-style TSV: validate the template on the blank-tape
run, then run the base from K(0^n; 0; b) (n = the real first-list length and small n) to its first undefined read and
print the token description of that configuration.
usage: python census.py HITS.tsv OUT.tsv [b values...]"""
import sys
from eng import *
src, outp = sys.argv[1], sys.argv[2]
bs = [int(x) for x in sys.argv[3:]] or [1, 2, 3, 6]
ST = 'ABCDEFGHIJ'
with open(outp, 'w') as fo:
    for line in open(src):
        f = line.rstrip('\n').split('\t')
        if len(f) < 3 or f[0].startswith('#') or f[0] == 'machine':
            continue
        grade, m, t = f[0], f[1], f[2]
        try:
            v = validate_template(m, t)
        except Fail as ex:
            print(grade, m, t, 'VALIDATION FAIL', ex, flush=True)
            fo.write('\t'.join([grade, m, t, 'VALFAIL', str(ex)]) + '\n'); continue
        T = v['T']; wm = work_machine(m, T)
        nreal = len(v['ds'])
        print(f'== {grade} {m} {t} first K at step {v["step"]}: ds={v["ds"][:3]}..(n={nreal}) a={v["a"]} b={v["b"]}', flush=True)
        for n in sorted({nreal, 2}):
            for b in bs:
                w = '0000' + kword(T, [0] * n, 0, b) + '0'
                r = run_to_event(wm, w, len(w) - 1, T['Q'], 20_000_000, T, minlen=len(w) + 6 * b + 12)
                if r[0] == 'T':
                    desc = f'n={n} b={b}: TIME {r[1]}'
                elif r[0] == 'K':
                    desc = f'n={n} b={b}: K-moment steps={r[1]} | {tokstr(tokens(r[2][:r[3]].lstrip("0")))} [{T["Q"]}]'
                else:
                    _, steps, word, h, q, c = r
                    L, R = word[:h], word[h + 1:]
                    desc = (f'n={n} b={b}: H {q}{c} steps={steps} | {tokstr(tokens(L.lstrip("0")))} [{q}{word[h]}] '
                            f'{tokstr(tokens(R.rstrip("0")))}')
                print('   ', desc, flush=True)
                fo.write('\t'.join([grade, m, t, str(nreal), desc]) + '\n')
