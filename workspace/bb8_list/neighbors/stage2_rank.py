"""Stage 2 growth ranking for unresolved neighbors: 2 and 10 CPU-second budgets (persistent Quick_Sim workers).

  ../../third_party/venv311/Scripts/python.exe stage2_rank.py stage2_unresolved.txt stage2_growth.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import fast_rank  # noqa: E402

PARENT = '1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---'


def dig(r):
    o = (r or {}).get('ones') or {}
    if o.get('kind') == 'integer':
        return len(o['decimal'])
    if o.get('kind') == 'large_integer':
        return round(o.get('bit_length', 0) * 0.30103)
    return -1


def diff(m):
    tr = lambda x: [t for row in x.split('_') for t in (row[:3], row[3:])]
    return ' '.join(f"{'ABCDEFGH'[i // 2]}{i % 2}:{a}->{b}" for i, (a, b) in enumerate(zip(tr(PARENT), tr(m))) if a != b)


def main():
    ms = [l.strip() for l in open(sys.argv[1]) if '_' in l]
    out = {}
    for T in (2, 10):
        pool = fast_rank.Pool(workers=2, sim_time=T, hard_timeout=5 * T + 60)
        try:
            for r in pool.rank(ms):
                out.setdefault(r['machine'], {})[T] = {'d': dig(r), 'loops': r.get('loops'), 'reason': r.get('reason')}
        finally:
            pool.close()
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
    for m, v in sorted(out.items(), key=lambda kv: -kv[1][10]['d']):
        a, b = v[2], v[10]
        d2 = a['d'] / a['loops'] if a['loops'] else 0
        d10 = b['d'] / b['loops'] if b['loops'] else 0
        print(f"{a['d']:>6}/{b['d']:>6} digits  dpl {d2:5.2f}->{d10:5.2f}  {str(b['reason'])[:22]:22s} {diff(m)}")


if __name__ == '__main__':
    main()
