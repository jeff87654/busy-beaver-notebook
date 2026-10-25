"""Fill loopvar/sec10_template.txt with current tallies and put it into report_body.txt as section 10; then run
gen_report.py.  python loopvar/fill_sec10.py"""
import collections, subprocess, sys
from pathlib import Path
H = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(H))
import tally
def tal(fn, total=None):
    c = collections.Counter(); n = 0
    p = H / fn
    for l in (p.read_text().splitlines() if p.exists() else []):
        f = l.split('\t'); r = f[2]; n += 1
        if r.startswith('RESULT FAIL'):
            k = 'chaotic FAIL (no period in the accumulator)' if ('no period' in r or 'disagree' in r or 'validation' in r) else 'simulator FAIL'
        else:
            k = tally.category(r)
        c[k] += 1
    s = ', '.join(f'{v} {k}' for k, v in c.most_common())
    return f'{n}{"/" + str(total) if total else ""} done: {s}' if n else 'not started'
t = (H / 'loopvar' / 'sec10_template.txt').read_text()
t = t.replace('@R3LATE@', tal('results_r3late.tsv', 90))
n0 = len({l.split('\t')[1] for l in (H.parent / 'bb10_from_bb7' / 'rec14_0RH' / 'watch_hits.tsv').read_text().splitlines()
          if l.split('\t')[0] in ('NOBOUNDARY', 'R4-SOME', 'HALT?')})
t = t.replace('@SIB0RH@', 'NOBOUNDARY / R4-SOME / HALT? rows: ' + tal('results_0RH.tsv', n0))
body = (H / 'report_body.txt').read_text(encoding='utf-8')
i = body.find('\n## 10.')
body = (body if i < 0 else body[:i]).rstrip('\n') + '\n\n' + t
(H / 'report_body.txt').write_text(body, encoding='utf-8')
subprocess.run([sys.executable, str(H / 'gen_report.py')], cwd=H)
print(t[t.find('@') - 20:] if '@' in t else 'filled')
