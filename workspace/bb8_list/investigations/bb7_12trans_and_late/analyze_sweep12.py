import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
import idle
from collections import Counter, defaultdict

def main():
    with open('sweep12_survivors.tsv') as f:
        header = f.readline().rstrip('\n').split('\t')
        rows = [dict(zip(header, line.rstrip('\n').split('\t'))) for line in f if line.strip()]

    print(f"Total survivors in sweep12_survivors.tsv: {len(rows)}")
    orig = {r['machine']: r for r in rows if r['mut_desc'] == 'ORIG'}
    muts = [r for r in rows if r['mut_desc'] != 'ORIG']
    print(f"  ORIG controls: {len(orig)}, Mutated survivors: {len(muts)}")

    # 1. Literal halters (>= 200k steps)
    lit_halts = [r for r in muts if r['halted'] == '1']
    print(f"\n1. Late literal halters (200k..2M steps): {len(lit_halts)}")
    for r in sorted(lit_halts, key=lambda x: -int(x['steps']))[:15]:
        print(f"   {r['machine']} (from {r['parent']} [{r['mut_desc']}]) -> HALT at {r['steps']} steps, ones={r['ones']}, span={r['span']}")

    # 2. Check for any candidate on a HALTS/CHAMPION parent that increases max_nd!
    print("\n2. Mutated survivors on HALTS / CHAMPION parents:")
    champ_muts = [r for r in muts if ('HALT' in r['parent_verdict'] and 'NEVER' not in r['parent_verdict']) or r['parent_grade'] == 'CHAMPION']
    print(f"   Count: {len(champ_muts)}")
    better_nd = []
    for r in champ_muts:
        p_nd = int(orig.get(r['parent'], {}).get('max_nd', 0))
        c_nd = int(r['max_nd'])
        if c_nd >= p_nd and c_nd >= 5:
            better_nd.append((c_nd, p_nd, r))
    better_nd.sort(key=lambda x: (-x[0], x[2]['machine']))
    print(f"   With max_nd >= parent_max_nd (and >= 5): {len(better_nd)}")
    for c_nd, p_nd, r in better_nd[:30]:
        print(f"   nd={c_nd} (parent={p_nd}) | {r['machine']} | {r['mut_desc']} | E0={r['E0_pat']} E1={r['E1_pat']} | {r['best_cfg']}")

    # 3. Candidates with BOTH 'H' and 'K' in E0_pat or E1_pat (X33-type parity flip candidates!)
    mixed_E = []
    pure_H_E = []
    for r in muts:
        if r['halted'] == '1':
            continue
        e0, e1 = r['E0_pat'], r['E1_pat']
        if ('H' in e0 and 'K' in e0) or ('H' in e1 and 'K' in e1):
            mixed_E.append(r)
        elif (e0 != '-' and set(e0) == {'H'}) or (e1 != '-' and set(e1) == {'H'}):
            pure_H_E.append(r)

    print(f"\n3. Pure-H exhaustion survivors (all-H in E0 or E1): {len(pure_H_E)}")
    for r in sorted(pure_H_E, key=lambda x: -int(x['max_nd']))[:25]:
        print(f"   nd={r['max_nd']} reb={r['n_rebuilds']} | {r['machine']} ({r['mut_desc']}) | parent={r['parent_verdict'][:25]} | E0={r['E0_pat']} E1={r['E1_pat']} | {r['best_cfg']}")

    print(f"\n4. Mixed H/K exhaustion survivors (parity-flip / rebuild-then-halt candidates): {len(mixed_E)}")
    for r in sorted(mixed_E, key=lambda x: (-int(x['max_nd']), x['machine']))[:35]:
        print(f"   nd={r['max_nd']} reb={r['n_rebuilds']} | {r['machine']} ({r['mut_desc']}) | parent={r['parent_verdict'][:25]} | E0={r['E0_pat']} E1={r['E1_pat']} | {r['best_cfg']}")

    # 5. Any candidate with max_nd >= 20 regardless of E_pat
    big_nd = [r for r in muts if int(r['max_nd']) >= 20 and ('H' in r['E0_pat'] or 'H' in r['E1_pat'] or 'T' in r['E0_pat'])]
    print(f"\n5. Candidates with max_nd >= 20 and H/T in E_pat: {len(big_nd)}")
    for r in sorted(big_nd, key=lambda x: -int(x['max_nd']))[:25]:
        print(f"   nd={r['max_nd']} reb={r['n_rebuilds']} | {r['machine']} ({r['mut_desc']}) | E0={r['E0_pat']} E1={r['E1_pat']} | {r['best_cfg']}")

if __name__ == '__main__':
    main()
