"""mk_final.py: build ../tier1_real.tsv (one row per machine) from members.tsv, labels.tsv, clusters.tsv,
realrun_15.tsv, sm/smsum.tsv and the targeted-scan conclusions below."""
import collections
H = '.'
mem = [l.rstrip('\n').split('\t') for l in open('members.tsv')]
lab = {l.split('\t')[0]: l.rstrip('\n').split('\t')[2] for l in open('labels.tsv')}
clu = {}
for l in open('clusters.tsv'):
    rs, name, coding, size, kind = l.rstrip('\n').split('\t')
    for part in rs.split(','):
        a, b = (part.split('-') + [part])[:2]
        for r in range(int(a), int(b) + 1): clu[str(r)] = (name, coding, size, kind)
rr = {}
for l in open('realrun_15.tsv'):
    f = l.rstrip('\n').split('\t'); rr[f[1]] = (f[3], f[5].split(' ')[0] if f[5] else '')
slow = {'1RB0RC_0RC1RA_1LD0RF_0LE0LF_0RA1LD_0LA0RG_0RA---': '1e11', '1RB0RC_1LB1RA_1LD0RF_0LE0LF_0RA1LD_0LA0RG_0RA---': '1e11',
        '1RB1RB_1RC0RA_1LD0RB_0LA1LE_1LE1LF_0RF1LG_0LC---': '1e10'}
sm = {l.split('\t')[1]: l.rstrip('\n').split('\t') for l in open('sm/smsum.tsv')}
H1F = {'1RB1RE_1RC1RA_0LD1LE_1RE1LE_0RG0RF_---0LG_1LC1RA': 'h1', '1RB1RF_0LC1LD_1RD1LD_0RE0RG_1LB1RF_1RA1RD_---0LE': 'h1',
       '1RB---_0RC0RA_0RD1LG_0LE1RC_1RF0LF_1LE1LD_0LD0LB': 'c01', '1RB---_0RC0RA_0RD1LG_0LE1RC_1RF0LF_1LE1LD_0RD0LB': 'c02'}
out = open('../tier1_real.tsv', 'w')
out.write('machine\trow\tgroup\tcluster\tcoding\tsize_class\treal_run\tresidue_basis\treal_class_branch\tverdict\tevidence\n')
cnt = collections.Counter()
for f in mem:
    row, rep, m = f[0], f[1], f[2]
    name, coding, size, kind = clu[row]
    st, steps = rr.get(m, ('?', ''))
    real = f'no halt to {slow.get(m, steps or "1e12+")} steps' 
    s = sm[m]; pc = s[2]; pdet = s[3] + ((' halts:' + s[4]) if s[4] else '')
    probe = f'probe(80 class variants: K2/3/4/6 x mod 2..36) {pc}: {pdet}'
    if kind == 'H1':
        t = H1F[m]
        if t == 'h1':
            basis = 'ACC N at exhaustion (cfg D1|[11]01^N); end form N mod 4'
            br = 'REBUILD to natural start shape for N=1..2000,10000..10047 (N=2: loops); borrows CONTINUE (16 templates x ACC 1..300)'
            ev = 'hand/real/h1/exN_all.txt, b_B*.txt' + ('; H2 = H1 relabelled, start 1 step later' if m.startswith('1RB1RF') else '')
        else:
            basis = 'ACC N at exhaustion (cfg C0|01^N[00] c01 / [01] c02); end form N mod 2'
            br = 'REBUILD for N=2..1200,6000..6023 (c01) / 1..600,3000..3015 (c02) (N=1,4,5 resp. 3,4: no halt); borrows CONTINUE (14 templates x ACC grid)'
            ev = 'hand/real/c01/exN.txt, exN_c02.txt, b_c02_*.txt'
        verdict = 'CLASS-INDEPENDENT REBUILD'
    elif kind == 'H4':
        basis = 'ACC N at final exhaustion (cfg G1|[10]01^N 00 10, H4 naming)'
        br = 'REBUILD of an ACC-sized hierarchical list for N=1..1000 (H4) / 1..400 (relatives) and ACC|(1,1) A=1..400; borrows CONTINUE (14 templates)'
        verdict = 'CLASS-INDEPENDENT REBUILD'; ev = 'hand/real/h4/'
    elif kind == 'L1':
        basis = 'ACC pair (b,a) at list exhaustion; d1/d2 residues (lead l1/)'
        br = 'lead: REBUILD for all (b,a) 1..24^2; ' + probe
        verdict = 'UNDECIDED'; ev = 'nonlist/l1/, notes.txt; hand/real/sm/'
    elif kind == 'M1':
        basis = 'L2 length m, final list n at L1 exhaustion'
        br = 'groupB: HALT for m=0..10, n=4..8 (no residue gate seen); ' + probe
        verdict = 'CLASS-INDEPENDENT HALT (narrow hand scan)'; ev = 'hand/groupB.txt M1; hand/real/sm/'
    elif kind == 'M2':
        basis = 'parity of the eater counter c at the end of the eat (groupB: c=3 HALT, c=4 REBUILD)'
        br = 'real class not computed: from the real 1e16 tape (c=84, d=6, list 54) with ACC reduced, c reaches 93 after eating d+list but the end of the eat needs ~2^90 steps; ' + probe
        verdict = 'UNDECIDED'; ev = 'hand/groupB.txt M2; hand/real/m2 (notes)'
    elif kind == 'C671':
        basis = 'ACC, G1.c, b at list/P exhaustion'
        if row == '11' and m == rep:
            br = 'targeted list-exhaustion scan on c09: CONTINUE (P=01^2 kept, G1 refilled) for c=1..3 x a=1..60 x b=1,7,20 (540 classes); ' + probe
            ev = 'hand/real/c09/s1.txt; hand/real/sm/'
        else:
            br = 'cluster rep c09: CONTINUE in 540 classes; ' + probe
            ev = 'hand/real/c09/s1.txt (rep); hand/real/sm/'
        verdict = 'CLASS-INDEPENDENT CONTINUE (probe)' if pc == 'NONE' else 'UNDECIDED'
    else:
        ev = 'hand/group report; hand/real/sm/'
        if name == 'segcopy':
            basis = '-'; br = 'LITERAL: digit-k exhaustion reached in the real run (~4.9e6 macro); list of 221185 items built, then identical segments appended (seen to 3e13 steps); ' + probe
            verdict = 'REBUILDS (literal)'; ev = 'hand/real/realrun_15.tsv; hand/groupA.txt'
        elif name == 'M6':
            basis = '-'; br = 'no exhaustion: each round appends an identical segment (bouncer-like); probe halts are from cutting the 110588 runs; ' + probe
            verdict = 'CONTINUES (no exhaustion)'; ev = 'hand/groupB.txt M6'
        elif name == 'C4075':
            basis = '-'; br = 'LITERAL: phase ends (D=0 -> ACC frozen, new D ~ ACC) occur in the real run; nothing counts phases (no top structure); ' + probe
            verdict = 'CONTINUES (literal)'; ev = 'hand/groupD.txt C4075; realrun_15.tsv'
        elif pc == 'NONE':
            basis = 'counters at first top exhaustion (not isolated)'; br = 'no halt in any probe class: ' + probe
            verdict = 'CLASS-INDEPENDENT CONTINUE (probe)'
        else:
            basis = 'probe halting moduli (see branch)'; br = 'class-dependent in probe: ' + probe
            if name == 'C15': br = 'groupD: y-exhaustion HALT (a=3,b=21 class) or REBUILD by class; ' + br
            verdict = 'UNDECIDED'
    cnt[verdict] += 1
    out.write('\t'.join([m, row, lab[row], name, coding, size, real, basis, br, verdict, ev]) + '\n')
print(cnt, sum(cnt.values()))
