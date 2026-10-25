"""final.py: merge rank7 / reb7 / mrounds / growth / S4 subagent / fam agents into final.tsv + counts."""
import json, collections, re
J = [l.rstrip('\n').split('\t') for l in open('joined.tsv')][1:]
mr = {json.loads(l)['machine']: str(json.loads(l)['verdict']) for l in open('mr.jsonl')}
reb = {json.loads(l)['machine']: str(json.loads(l)['verdict']) for l in open('reb_all.jsonl')}
gr = {l.split('\t')[0]: l.split('\t')[1] for l in open('growth.tsv')}
blk = {l.split()[0]: l.split() for l in open('blk.txt')}
s4 = {}
for i in range(4):
    fam = collections.defaultdict(list)
    for l in list(open('nofit_s4/slice%d.tsv' % i))[1:]:
        f = l.split('\t'); fam[f[0]].append(f[1])
    for l in list(open('nofit_s4/s%d/RESULT.tsv' % i))[1:]:
        f = l.rstrip('\n').split('\t'); fid = re.match(r'F\d+\.\d+', f[0]).group(0)
        for m in fam.get(fid, []): s4.setdefault(m, 'S4:' + f[4][:40])
t14 = set(l.strip() for l in open('famT14/rows16.txt') if l.strip()) | {
    '1RB1LG_0RC0LB_1RD0RF_1LE---_1RF1RE_0LA0LG_0RH1LA_0RE1RC', '1RB1LG_0RC0LB_1RD0RH_1LE1RC_1RF1RE_0LA0LG_0RD1LA_---0RE'}
f0ld = {'1RB0LD_0RC---_1LC0RD_1LE1LE_0LF1LA_1LG0LG_1RH1RC_1LD1RG', '1RB0LD_0RC---_1LC0RD_1LF1LE_0LF1LA_1LG0LG_1RH1RC_1LD1RG',
        '1RB0LD_0RC---_1LC0RD_0RF1LE_0LF1LA_1LG0LG_1RH1RC_1LD1RG'}
cnt = collections.Counter()
with open('final.tsv', 'w', newline='\n') as o:
    o.write('rank\tmachine\tgrade\trank7\tlevel\tfinal\tsource\n')
    for f in J:
        m = f[1]; r = reb.get(m, '-'); x = mr.get(m, '-')
        if m in f0ld: v, s = 'HALTS-SMALL (<=2^^7)', 'fam0LD'
        elif m in t14: v, s = 'NEVER-HALTS (rebuild-forever)', 'famT14'
        elif x != '-' and not x.startswith('UNSETTLED'): v, s = x.split('(')[0] + ('(multi HALT@2: H8 family, small)' if x.startswith('HALT') else '(residue,multi)'), 'mrounds'
        elif m in s4: v, s = s4[m], 'S4'
        elif r.startswith(('NEVER', 'HALT')): v, s = r.split('+')[0][:40], 'reb7'
        elif r.startswith('NOFIT'):
            b = blk.get(m)
            if b and b[7] == 'HALT': v, s = 'HALTS-SMALL (literal <3e8)', 'blk'
            else: v, s = 'NOT-RECORD-CLASS (LOW-GROWTH)' if gr.get(m) == 'LOW-GROWTH' else ('LOW-SPAN (<=200 cells @3e8)' if b else '?'), 'growth/blk'
        elif 'MAX' in r: v, s = 'NEVER-HALTS? (every round rebuilds, class 0 mod 1; round cap)', 'reb7'
        else: v, s = 'UNSETTLED: ' + (x if x != '-' else r)[:50], 'all tools'
        k = v.split(' ')[0].split('(')[0].rstrip(':')
        cnt[k] += 1
        o.write('\t'.join([f[0], m, f[2], f[3].split('+')[0], f[4], v, s]) + '\n')
for k, c in cnt.most_common(): print(c, k)
