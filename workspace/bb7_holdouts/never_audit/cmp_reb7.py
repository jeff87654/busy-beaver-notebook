"""cmp_reb7.py JSONL: side-by-side of my measured rules/exhaustion and reb7's fitted rules/exhaustion map per row."""
import sys, json, csv
ver = {r['machine']: r for r in csv.DictReader(open('../reb7/final_all_verdicts.tsv'), delimiter='\t')}
for l in open(sys.argv[1]):
    d = json.loads(l); m = d['machine']; r = ver.get(m, {})
    print('==', m, '|', d.get('template'), '|', d.get('verdict', '')[:90])
    print('   mine : D %s | B1 %s | B5 %s | E halt %s rebuild %s' % (d.get('rule0'), d.get('rule1'), d.get('rule5'),
          (d.get('halt_classes') or [])[:8], (d.get('rebuild') or [''])[0][:60]))
    print('   reb7 : %s | %s | %s' % (r.get('rules', '-')[:110], r.get('exhaustion', '-')[:80], r.get('verdict', '-')[:40]))
