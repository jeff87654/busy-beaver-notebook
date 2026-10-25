import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from collections import Counter, defaultdict

def short_verdict(v):
    if v.startswith('NOT-RECORD-CLASS'):
        return v.split(')')[0] + ')'
    return v.split('(')[0].split('+')[0]

def main():
    rows = []
    with open('census12_all.tsv') as f:
        header = f.readline().rstrip('\n').split('\t')
        for line in f:
            if not line.strip():
                continue
            parts = line.rstrip('\n').split('\t')
            rows.append(dict(zip(header, parts)))

    print(f"Total machines in census12_all.tsv: {len(rows)}")
    by_v = Counter(short_verdict(r['verdict']) for r in rows)
    print("Verdict breakdown:", dict(by_v))

    # Focus on non-LOW-GROWTH machines (and also report overall)
    for subset_name, pred in [
        ("ALL 1,797 MACHINES", lambda r: True),
        ("NON-LOW-GROWTH (882 MACHINES: NEVER-HALTS, HALTS, POLY, f4/counter)", lambda r: 'LOW-GROWTH' not in r['verdict']),
        ("NEVER-HALTS + HALTS (794 MACHINES)", lambda r: short_verdict(r['verdict']) in ('NEVER-HALTS', 'HALT-REACHED', 'HALTS-SMALL')),
    ]:
        sub = [r for r in rows if pred(r)]
        print(f"\n=== {subset_name} (n={len(sub)}) ===")
        print("  n_used_total     :", dict(sorted(Counter(int(r['n_used_total']) for r in sub).items())))
        print("  n_used_after_5k  :", dict(sorted(Counter(int(r['n_used_after_5k']) for r in sub).items())))
        print("  n_used_after_100k:", dict(sorted(Counter(int(r['n_used_after_100k']) for r in sub).items())))
        print("  n_engine         :", dict(sorted(Counter(int(r['n_engine']) for r in sub).items())))

        le12 = [r for r in sub if int(r['n_engine']) <= 12 or int(r['n_used_after_5k']) <= 12]
        print(f"  Machines with n_engine <= 12 or n_used_after_5k <= 12: {len(le12)}")
        role_types = Counter()
        for r in le12:
            for item in r['non_engine_slots'].split(';'):
                if ':' in item:
                    slot, role = item.split(':', 1)
                    role_key = role.split('(')[0]
                    role_types[role_key] += 1
        print("  Non-engine slot role counts:", dict(role_types))

    # Write detailed list of non-low-growth machines with <= 12 engine transitions
    cands = [r for r in rows if 'LOW-GROWTH' not in r['verdict'] and (int(r['n_engine']) <= 12 or int(r['n_used_after_5k']) <= 12)]
    with open('census12_candidates.tsv', 'w', newline='\n') as fo:
        cols = ['machine', 'grade', 'verdict', 'stage', 'n_used_total', 'n_used_after_5k', 'n_used_after_100k', 'n_engine', 'non_engine_slots', 'span', 'template', 'rules', 'exhaustion']
        fo.write('\t'.join(cols) + '\n')
        for r in sorted(cands, key=lambda x: (int(x['n_engine']), short_verdict(x['verdict']), x['machine'])):
            fo.write('\t'.join(r[c] for c in cols) + '\n')
    print(f"\nWrote {len(cands)} non-low-growth <=12-transition candidates to census12_candidates.tsv")

    # Print some notable examples (HALTS, CHAMPION, etc.)
    print("\n--- Notable <=12-transition machines among HALTS / CHAMPION / NEVER-HALTS ---")
    for r in cands[:40]:
        print(f"  {r['machine']} | {r['grade']} | {short_verdict(r['verdict'])} | eng={r['n_engine']} after5k={r['n_used_after_5k']} tot={r['n_used_total']} | {r['non_engine_slots']}")

if __name__ == '__main__':
    main()
