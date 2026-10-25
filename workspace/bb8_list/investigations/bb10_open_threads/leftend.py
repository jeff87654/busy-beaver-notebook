"""Thread 1: the left-end event of the g-type conveyor machines with the conveyor's tail.
  python leftend.py machines.txt out.tsv [MAXSTEPS]
Start: 11 D1^m | a = D1 | r = D(r) | conveyor tail D0^6 (1 00 D0^5)^T 1 00 1 00 D0, head right in state B
(the exhausted prefix: K(0^m; 0; r) followed by the conveyor tail).  Grid m in {1, 3}, r in {8, 9, 10, 20}, T in {8, 12}.
For each run: H (halt) / T, the longest run of one repeated token value >= 4 seen in any canonical configuration
(a rebuilt list), and the last configuration."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tv  # noqa: E402

TAIL = 'D(0)^{6} (1^1 0^2 D(0)^{5})^{%d} 1^1 0^2 1^1 0^2 D(0)'


def longest_run(body):
    best = (0, None)
    for tok in body.split():
        m = re.fullmatch(r'(\d+)\*(\d+)', tok)
        if m and int(m.group(1)) >= 4 and int(m.group(2)) > best[0]:
            best = (int(m.group(2)), int(m.group(1)))
    return best


def main():
    ms = [l.split()[0] for l in Path(sys.argv[1]).read_text().splitlines() if l.strip()]
    maxsteps = int(sys.argv[3]) if len(sys.argv) > 3 else 300_000_000
    with open(sys.argv[2], 'w') as out:
        for mach in ms:
            for m in (0, 1, 2, 3):
                for r in (9, 20):
                    for T in (8,):
                        cfg = f'D(0)^{{2}} D(1)^{{{m}}} D(1) D({r}) ' + TAIL % T
                        best, last, kind = (0, None), '', ''
                        for line in tv.run(mach, cfg, {}, maxsteps, ['-q', 'B', '-m', '200000', '-r', '9', '-k', '1'], raw=True):
                            if ' | ' not in line:
                                continue
                            head, body = line.split(' | ', 1)
                            lr = longest_run(body)
                            if lr[0] > best[0]:
                                best = lr
                            if head[0] in 'HTM':
                                kind, last = head, body[:160]
                        out.write(f'{mach}\tm={m} r={r} T={T}\t{kind}\tlist={best[0]}xD({best[1]})\t{last}\n')
                        out.flush()


if __name__ == '__main__':
    main()
