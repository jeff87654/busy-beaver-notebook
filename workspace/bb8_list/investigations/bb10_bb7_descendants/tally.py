"""Final tallies for the report: rec14 rebuilders by category (machine-weighted, with class counts and tags) and
c35m14 screen / follower results.  python tally.py > tally.txt"""
import re
from collections import OrderedDict, Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_results(*fns):
    res = {}
    for fn in fns:
        p = HERE / fn
        if not p.exists():
            continue
        for l in p.read_text().splitlines():
            f = l.split('\t')
            if len(f) >= 3:
                res[f[0]] = f[2]
    return res


ORDER_BROKEN = {'1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RI0LC_1RG1LD_0RH0RF_---0RE_0LJ0LI_0RE0RC',
                '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_---0RE_0RJ1RD_1LI0RI'}


def category(line):
    if line is None:
        return 'NOT-RUN'
    if any(m in line for m in ()):
        pass
    r = re.search(r'RESULT (\S+)', line).group(1).replace('UNCLEAR-', '')
    fc = int(re.search(r'full_cycles=(\d+)', line).group(1)) if 'full_cycles=' in line else 0
    st = int(re.search(r'stages=(\d+)', line).group(1)) if 'stages=' in line else 0
    lv = int(re.search(r'level=(\d+)', line).group(1)) if 'level=' in line else (1 if fc else 0)
    if 'level=' not in line and fc >= 3 and re.search(r'stages=9 full_cycles=6', line):
        lv = 2      # pre-level runs of the n -> n + 4R loopers (checked by hand in the logs)
    if r == 'HALT':
        if lv >= 2:
            return 'RECORD-CANDIDATE (halts at omega-level >= 2)'
        if fc >= 1:
            return f'ONE-REBUILD (omega-level 1, {fc} full cycle(s))'
        return 'CHAMPION-LIKE' if st == 1 else 'GROUP-1-LIKE'
    if r == 'LOOP' and fc >= 1:
        return 'INFINITE-REBUILDS (loop)'
    if lv >= 2:
        return f'INFINITE-REBUILDS? ({r} at omega-level >= 2)'
    if fc >= 1:
        return f'UNCLEAR-{r} after {fc} full cycle(s)'
    if 'hyb10 gave no output' in line:
        return 'NON-HALT (runaway, tape > 4e6 cells)'
    return f'UNCLEAR-{r}'


def main():
    cls = OrderedDict()
    for l in (HERE / 'sigs2_all.tsv').read_text().splitlines():
        m, s = l.split('\t')
        cls.setdefault(s, []).append(m)
    tag = {}
    for fn in ('set_r1.tsv', 'set_r2.tsv'):
        for l in (HERE / fn).read_text().splitlines():
            f = l.split('\t')
            tag.setdefault(f[0], f[1])
    res = load_results('results_r1.tsv', 'results_reps.tsv', 'results_cls.tsv', 'results_pkl.tsv', 'results_mem.tsv', 'results_redo.tsv')
    per_machine = {}
    for s, ms in cls.items():
        ref = next((res[m] for m in ms if m in res), None)
        for m in ms:
            own = res.get(m)
            per_machine[m] = (category(own) if own else category(ref) + ('' if ref is None else ' [by class]'))
            if m in ORDER_BROKEN:
                per_machine[m] = 'UNCLEAR-ORDER (fit subtracts accumulators)'
    tally = Counter(v.replace(' [by class]', '') for v in per_machine.values())
    own = Counter(v for v in per_machine.values() if '[by class]' not in v)
    print('rec14 rebuilders (round 1 + round 2):', len(per_machine), 'machines,', len(cls), 'behaviour classes')
    for c, n in sorted(tally.items(), key=lambda x: -x[1]):
        print(f'  {c:52s} {n:5d}   (own follower run: {own[c]})')
    print(f'  machines with their own follower run: {sum(own.values())}; inferred from their class: '
          f'{sum(tally.values()) - sum(own.values())}')
    bytag = defaultdict(Counter)
    for m, c in per_machine.items():
        bytag[tag.get(m, '?')][c.replace(' [by class]', '')] += 1
    print('by watcher/bign tag:')
    for t, cc in sorted(bytag.items()):
        print(f'  {t}: ' + ', '.join(f'{c}={n}' for c, n in sorted(cc.items(), key=lambda x: -x[1])))
    print('notable (own runs):')
    for m, line in res.items():
        c = category(line)
        if c.startswith(('ONE-REBUILD', 'RECORD', 'INFINITE')) or 'full cycle' in c:
            print(f'  {c:40s} {m}  {line[:140]}')
    # c35m14
    sc = (HERE / 'c35screen.tsv')
    if sc.exists():
        rows = [l.split('\t') for l in sc.read_text().splitlines()]
        reclike = [r for r in rows if len(r) > 3 and r[3].startswith('4*34 1 ')]
        e0def = [r for r in reclike if r[0].split('_')[4][:3] != '---']
        print(f'c35m14: {len(rows)} holdouts screened; {len(reclike)} reproduce the BB(8) record run; {len(e0def)} of them have E0 defined')
        r35 = load_results('results_c35.tsv')
        cc = Counter(category(r35.get(r[0])) + (' ' + re.search(r"ones=(\S+)", r35[r[0]]).group(1) if r[0] in r35 and 'ones=' in r35[r[0]] else '') for r in e0def)
        for c, n in sorted(cc.items(), key=lambda x: -x[1]):
            print(f'  {c:52s} {n}')


if __name__ == '__main__':
    main()
