import os
import sys
os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ.get('PATH', '')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
import idle
import argparse
import fit7, eng7, rounds7, reb7

def replace_P(tmpl_str, new_P):
    parts = tmpl_str.split(',')
    out = []
    for p in parts:
        if p.startswith('P='):
            out.append('P=' + (new_P if new_P else '-'))
        else:
            out.append(p)
    return ','.join(out)

# Check all NO-K classes from sweep12_analyzed.txt with stripped leading zeros on obs_O
with open('sweep12_survivors.tsv', encoding='utf-8') as f:
    hdr = f.readline().rstrip('\n').split('\t')
    rows = [dict(zip(hdr, line.rstrip('\n').split('\t'))) for line in f if line.strip()]
by_m = {r['machine']: r for r in rows}

nok_machines = [
    '1RB1RF_1RB0RF_1LD1LA_0LE1LE_1LG0LA_1RE0RC_---1LC',
    '1RB0LC_1LC1LA_0LD0LB_0RE0RG_1RF1LE_0LD0RA_1RD---',
    '1RB---_1RC1RA_0LD0LE_1RA0LE_0RF1LC_1RG0RC_0RC1RE',
    '1RB---_1RC1RA_0LD0LE_1RA0LE_0RF1LC_1RG1RA_0RC1RE',
    '1RB---_1RC1RA_0LD0LE_1RA0LE_0RF1LC_1RG0RC_0LE1RE',
    '1RB---_1RC1RA_0LD0LE_1RA0LE_0RF1LC_1RG1RA_0LE1RE',
    '1RB0LE_1RC---_1RD1RB_0LA0LE_0RF1LD_1RG0RD_0RD1RE',
    '1RB0LE_1RC---_1RD1RB_0LA0LE_0RF1LD_1RG1RB_0RD1RE',
    '1RB1RF_1RA0RF_1LD1LA_0LE1LE_1LG0LA_1RE0RC_---1LC',
    '1RB0LE_1RC---_1RD1RB_0LA0LE_0RF1LD_1RG0RD_0LE1RE',
    '1RB0LE_1RC---_1RD1RB_0LA0LE_0RF1LD_1RG1RB_0LE1RE',
]

dummy_args = argparse.Namespace(steps=10000000, maxk=1000, rand=10)
for m in nok_machines:
    r = by_m[m]
    obs_O = r['obs_O'].lstrip('0') if r['obs_O'] != '-' else ''
    tmpl2 = replace_P(r['template'], obs_O)
    res = reb7.analyse(m, tmpl2, dummy_args, False)
    print(f"=== {m} [{r['mut_desc']}] nd={r['max_nd']} obs_O={r['obs_O']} -> P={obs_O or '-'} ===")
    print(f"  verdict={res.get('verdict')} nK={res.get('nK')} first_K={res.get('first_K')} last_K={res.get('last_K')}")
    print(f"  rules  ={res.get('rules')}")
    print(f"  E      ={res.get('E0') or res.get('E')}")
    print(f"  marker ={res.get('marker')} nE={res.get('nE')} mscan={res.get('mscan')}")
    if 'rounds' in res:
        print(f"  Q1     ={res['rounds'].get('80640', [None])[0]} trace={res['rounds'].get('80640', [None, []])[1][:4]}")
        print(f"  Q2     ={res['rounds'].get('483840', [None])[0]} trace={res['rounds'].get('483840', [None, []])[1][:4]}")
