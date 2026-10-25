"""9-state redirect roots built from 8-state champion-rule machines.

Goal: a 9-state machine that rebuilds its digit list once and halts at the next exhaustion (a "switch" in the
new state I).  Halting after one rebuild of the 30-digit rebuilders would give roughly f_omega(2^^31 3), above the
BB(9) champion's f_omega(f_9(2)).  Item 1 showed that no 8-state neighbour can do this, because every transition is
shared with the digit rules; the 9th state is the missing freedom.

The enumerator branches a free transition only when the run reaches it, and the first rebuild comes after more than
2^^31 steps, so freeing the halt slot alone does nothing.  Each root therefore frees ONE transition t of the
parent (one the start-up reaches early; A0 stays 1RB) together with the parent's undefined slot and the new state I
(row `------`).  `knuth9.exe exactfrom ROOT 8 2 C OUT` then enumerates every completion: t rewired to any value,
including into I, and I's two transitions whenever they are reached.

  python gen_roots9.py > roots9.tsv     # root <TAB> free count <TAB> parent label <TAB> freed transition
"""
PARENTS = {
    'p0': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1RF',   # 30-digit rebuilder
    'p1': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1RH',   # 30-digit rebuilder
    'p2': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0LH0RF_---1RE',   # 11-digit rebuilder
    'p3': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0RH0RF_---1LE',   # 11-digit rebuilder
    'c35': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF',  # the 35-digit BB(8) champion
    'c35h': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LH',  # its 1LH sibling
}
ST = 'ABCDEFGHI'


def main():
    seen = set()
    for lab, p in PARENTS.items():
        cells = [r[3 * c:3 * c + 3] for r in p.split('_') for c in range(2)]
        for k in range(1, 16):                       # skip A0
            if cells[k] == '---':
                continue
            c = list(cells)
            c[k] = '---'
            rows = [c[2 * i] + c[2 * i + 1] for i in range(8)] + ['------']
            root = '_'.join(rows)
            if root in seen:
                continue
            seen.add(root)
            free = ''.join(rows).count('---')
            print(f'{root}\t{free}\t{lab}\t{ST[k // 2]}{k % 2}')


if __name__ == '__main__':
    main()
