"""Which reachable digit-list neighbours can halt at a rebuild (R4)?

  python rebuild_probe.py        reads reach.tsv, writes rebuild.tsv

A digit-list machine that halts when the list is used up and rebuilt (R4: K(; 0; b) -> ...) halts at the first
rebuild if it halts for every b, which gives a modest sigma (the first list is short). One that halts only for
some b can survive the first rebuild and halt at a later one, after a list of about b digits has been counted
down: that is the record-class scenario. This probes R4 from K(; 0; b) for b = 1..12 with dlscan.exe --probe
(1,000,000 steps each) for every machine of reach.tsv that showed family configurations with digits.
"""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXE = HERE.parent / 'dlscan.exe'
BS = range(1, 13)


def mirror(tm):
    return tm.translate(str.maketrans('LR', 'RL'))


def main():
    rows = [l.split('\t') for l in (HERE / 'reach.tsv').read_text().splitlines()[1:] if l.strip()]
    rows = [r for r in rows if int(r[5]) > 0]
    cases = []
    for r in rows:
        o, q, suf, u, sep = r[2].split(',')
        tm = mirror(r[0]) if o == 'L' else r[0]
        for b in BS:
            cases.append(f'{tm} {q} {suf} {u} {sep} - 0 {b}\n')
    inp = HERE / 'rebuild_cases.txt'
    inp.write_text(''.join(cases), newline='\n')
    out = subprocess.run([str(EXE), '--probe', str(inp), '1000000'], capture_output=True, text=True, check=True,
                         creationflags=getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)).stdout.splitlines()
    inp.unlink()
    assert len(out) == len(cases)
    summary = {}
    with open(HERE / 'rebuild.tsv', 'w', newline='\n') as f:
        f.write('machine\tgrade\tkey\tmax_digits\tR4_pattern\tR4_details\n')
        for i, r in enumerate(rows):
            res = out[i * len(BS):(i + 1) * len(BS)]
            pat = ''.join('H' if x.startswith('HALT') else 'K' if x.startswith('K') else 'T' for x in res)
            kind = ('halts for every b' if set(pat) == {'H'} else
                    'halts for some b' if 'H' in pat else
                    'never halts at R4' if set(pat) == {'K'} else 'timeouts')
            summary.setdefault((r[1], kind), []).append(r[0])
            f.write('\t'.join([r[0], r[1], r[2], r[6], pat, ' | '.join(res)]) + '\n')
    for (grade, kind), ms in sorted(summary.items()):
        print(f'{len(ms):5d}  {grade:10s}  {kind:20s}  e.g. {ms[0]}')


if __name__ == '__main__':
    main()
