import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
import json

pf_verdicts = {}
for line in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\counters\pf\final_list.tsv'):
    parts = line.rstrip('\n').split('\t')
    if len(parts) >= 5:
        m = parts[2]
        v = parts[3]
        note = parts[4]
        tmpl = '-'
        if 'with template ' in note:
            tmpl = note.split('with template ')[1].strip()
        elif 'L,F,P=11,u=011' in note:
            tmpl = 'L,F,P=11,u=011,s=0,d=1d+0,b=2b+1,S=01'
        elif 'L,E,P=11,u=011' in note:
            tmpl = 'L,E,P=11,u=011,s=0,d=1d+0,b=2b+1,S=01'
        pf_verdicts[m] = (v, note, tmpl)

run_f = {}
for fn in (r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\run_f0.jsonl',
           r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\run_f1.jsonl'):
    for line in open(fn):
        r = json.loads(line)
        run_f[r['machine']] = r

with open('pool7f_verdicts.tsv', 'w', newline='\n') as fo:
    fo.write('machine\tgrade\tsources\tverdict\tstage\tnote\ttemplate\trules\texhaustion\n')
    for line in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\pool7f.tsv'):
        f = line.rstrip('\n').split('\t')
        if f[0] == 'machine':
            continue
        m, tmpl_in, grade, sources, _ = f
        r = run_f.get(m, {})
        v = r.get('verdict', 'NOFIT')
        tmpl = r.get('tmpl', tmpl_in)
        rules = r.get('rules', '-')
        exh = r.get('E0') if r.get('marker') else (list((r.get('E') or {}).values()) or ['-'])[0]
        note = ''
        stage = 'S1'
        if m in pf_verdicts:
            pv, pnote, ptmpl = pf_verdicts[m]
            v = pv
            note = pnote
            if ptmpl != '-':
                tmpl = ptmpl
            stage = 'PF'
        fo.write(f'{m}\t{grade}\t{sources}\t{v}\t{stage}\t{note}\t{tmpl}\t{rules}\t{exh}\n')
print("Wrote pool7f_verdicts.tsv")
