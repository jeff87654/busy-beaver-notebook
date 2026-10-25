import os
import sys
os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ.get('PATH', '')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
import idle
import argparse
from concurrent.futures import ThreadPoolExecutor
from collections import Counter, defaultdict
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

def main():
    z_slots_map = {}
    r_slots_map = {}
    parent_info = {}
    for fn in ('census12_all.tsv', 'census12_pool7f.tsv'):
        with open(fn, encoding='utf-8') as f:
            hdr = f.readline().rstrip('\n').split('\t')
            for line in f:
                if not line.strip(): continue
                d = dict(zip(hdr, line.rstrip('\n').split('\t')))
                m = d['machine']
                parent_info[m] = d
                zs, rs = set(), set()
                if d['non_engine_slots'] != '-':
                    for item in d['non_engine_slots'].split(';'):
                        if ':' not in item: continue
                        sn, role = item.split(':', 1)
                        if role.startswith(('STARTUP_ONLY', 'EARLY_ONLY', 'UNUSED')) or ',vl=0,' in role:
                            zs.add(sn)
                        else:
                            rs.add(sn)
                z_slots_map[m] = zs
                r_slots_map[m] = rs

    with open('sweep12_survivors.tsv', encoding='utf-8') as f:
        hdr = f.readline().rstrip('\n').split('\t')
        rows = [dict(zip(hdr, line.rstrip('\n').split('\t'))) for line in f if line.strip()]

    orig_map = {r['machine']: r for r in rows if r['mut_desc'] == 'ORIG'}
    muts = [r for r in rows if r['mut_desc'] != 'ORIG' and r['halted'] == '0']

    z_only_muts = []
    has_H_muts = []
    for r in muts:
        p = r['parent']
        zs = z_slots_map.get(p, set())
        desc = r['mut_desc']
        body = desc.split(':', 1)[1]
        touched_slots = [kv.split('=')[0] for kv in body.split(',')]
        if desc.startswith('HREL:'):
            is_z = (touched_slots[1] in zs)
        else:
            is_z = all(s in zs for s in touched_slots)
        r['is_z_only'] = is_z
        if is_z:
            z_only_muts.append(r)
        if 'H' in r['E0_pat'] or 'H' in r['E1_pat']:
            has_H_muts.append(r)

    z_interesting = [r for r in z_only_muts if int(r['max_nd']) >= 3 and (
        'H' in r['E0_pat'] or 'H' in r['E1_pat'] or
        ('HALT' in r['parent_verdict'] and 'NEVER' not in r['parent_verdict']) or
        r['parent_grade'] == 'CHAMPION'
    )]

    to_test = {}
    for r in has_H_muts + z_interesting:
        to_test[r['machine']] = r

    # Group by (parent, best_cfg, E0_pat, E1_pat, obs_O) to collapse unreached 2nd-slot clones
    groups = defaultdict(list)
    for m, r in to_test.items():
        key = (r['parent'], r['best_cfg'], r['E0_pat'], r['E1_pat'], r['obs_O'])
        groups[key].append(r)

    reps = []
    for key, members in groups.items():
        # Prefer 1MUT or z_only representative
        members.sort(key=lambda x: (0 if x['is_z_only'] else 1, 0 if x['mut_desc'].startswith('1MUT') else 1, x['machine']))
        reps.append((key, members[0], len(members)))

    reps.sort(key=lambda x: (-int(x[1]['max_nd']), x[1]['machine']))
    print(f"Total candidates to test: {len(to_test)} -> collapsed into {len(reps)} distinct trajectory/E-pattern equivalence classes.")

    dummy_args = argparse.Namespace(steps=3000000, maxk=600, rand=5)

    def run_one(item):
        key, r, cnt = item
        m = r['machine']
        tmpl = r['template']
        obs_O = r['obs_O'].lstrip('0') if r['obs_O'] != '-' else ''
        res = reb7.analyse(m, tmpl, dummy_args, False)
        if res.get('verdict') in ('NOFIT', 'NO-K'):
            tmpl2 = replace_P(tmpl, obs_O)
            if tmpl2 != tmpl:
                res2 = reb7.analyse(m, tmpl2, dummy_args, False)
                if res2.get('verdict') not in ('NOFIT', 'NO-K'):
                    res = res2
        # Compute finalized verdict string as in reb7.py main
        v = res.get('verdict')
        if v is None:
            r1 = res['rounds'][str(reb7.Q1)][0]
            r2 = res['rounds'][str(reb7.Q2)][0]
            inv, inv_d = reb7.invariant_verdict(
                fit7.fit_rules(fit7.Prober(m, res['tmpl'])),
                None, ([], 0, 0), 0
            ) if False else (None, '')
            if res['growth'] in ('COUNTER', 'POLY'):
                v = f"NOT-RECORD-CLASS({res['growth']})"
            elif r1.startswith('LOOP') and r2.startswith('LOOP'):
                v = 'NEVER-HALTS(residue)+Q2'
            elif 'HALT' in r1 or 'HALT' in r2:
                v = f'HALT-REACHED({r1}/{r2})'
            else:
                v = f'UNSETTLED({r1}/{r2})'
            res['verdict'] = v
        return (key, r, cnt, res)

    results = []
    with ThreadPoolExecutor(2) as ex:
        for out in ex.map(run_one, reps):
            results.append(out)
            _, r, cnt, res = out
            print(f"  done {r['machine']} ({r['mut_desc']}, x{cnt}) -> {res.get('verdict')} [nd={r['max_nd']}]", flush=True)

    with open('sweep12_analyzed.txt', 'w', encoding='utf-8') as fo:
        fo.write(f"Total candidates: {len(to_test)} in {len(reps)} distinct classes\n\n")
        for key, r, cnt, res in results:
            p_nd = orig_map.get(r['parent'], {}).get('max_nd', '?')
            fo.write(f"CLASS (x{cnt}): rep={r['machine']} [{r['mut_desc']}] (z_only={r['is_z_only']})\n")
            fo.write(f"  Parent : {r['parent']} ({r['parent_grade']} | {r['parent_verdict']})\n")
            fo.write(f"  Sweep12: max_nd={r['max_nd']} (orig={p_nd}) reb={r['n_rebuilds']} E0={r['E0_pat']} E1={r['E1_pat']} best_cfg={r['best_cfg']}\n")
            fo.write(f"  reb7   : verdict={res.get('verdict')} growth={res.get('growth')} nK={res.get('nK')} first_K={res.get('first_K')} last_K={res.get('last_K')}\n")
            fo.write(f"  rules  : {res.get('rules', '-')}\n")
            fo.write(f"  E_map  : {res.get('E0') or res.get('E', '-')}\n")
            if 'rounds' in res:
                fo.write(f"  rounds : Q1={res['rounds'].get('80640', ['-'])[0]} trace={res['rounds'].get('80640', [None, []])[1][:4]}\n")
            if res.get('fit_fail') and res.get('verdict') == 'NOFIT':
                fo.write(f"  nofit  : {res.get('fit_fail')[:2]}\n")
            fo.write("\n")

    print("Wrote sweep12_analyzed.txt")

if __name__ == '__main__':
    main()
