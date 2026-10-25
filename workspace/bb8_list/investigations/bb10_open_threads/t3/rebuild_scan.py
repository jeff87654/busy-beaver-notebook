"""Thread 3: does the empty-list exhaustion K(;0;b) rebuild a list whose length grows with b?
  python rebuild_scan.py rows.tsv out.tsv [MAXSTEPS]
For each machine (template from the watcher) and b = 1..4: literal run from K(;0;b) (evt.exe, canonical state of the
template), the maximum number of items (repeats expanded) over all printed canonical configurations, and the halt
status.  A maximum that grows roughly linearly with the accumulator reached marks a length-expanding rebuild."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kprobe import run  # noqa: E402


def nitems(body):
    n = 0
    for tok in body.split():
        m = re.fullmatch(r'(.*)\*(\d+)', tok)
        n += int(m.group(2)) if m else 1
    return n


def main():
    rows = [l.split('\t') for l in Path(sys.argv[1]).read_text().splitlines() if l.strip()]
    ms = int(sys.argv[3]) if len(sys.argv) > 3 else 20_000_000
    with open(sys.argv[2], 'w') as out:
        for m, tpl in rows:
            res = []
            for b in (1, 2, 3, 4):
                o = run(m, tpl, [], 0, b, ms, ['-m', '100000', '-r', '9', '-k', '1'])
                best, bestline, end = 0, '', ''
                for l in o.splitlines():
                    if ' | ' not in l:
                        continue
                    head, body = l.split(' | ', 1)
                    k = nitems(body)
                    if k > best:
                        best, bestline = k, body.strip()[:150]
                    if head[0] in 'HTM':
                        end = head.split()[0] + '@' + head.split()[1]
                res.append(f'b={b}:max{best}:{end}')
                out.write(f'#  {m} b={b} max-items config: {bestline}\n')
            out.write(f'{m}\t{tpl}\t' + ' '.join(res) + '\n')
            out.flush()


if __name__ == '__main__':
    main()
