"""Run a machine from a constructed token configuration of g's merged-counter world and log events.
  python nxt.py MACHINE "TOKENS" X1,X2,.. STEPS [MODE] [NPRINT]
TOKENS: D-token list in front of the accumulator; Pn = g's prefix 0*2 4 9 6 210 14 10 + n groups (4 2 7).
The accumulator token D(X) and g's real tail (from endtoks_B6.txt) are appended; head in B on the right edge.
MODE: tr9 mode (default deadend), output abbreviated (PFX = prefix + groups, TAIL = repeated tail units)."""
import re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
G2 = HERE.parent / 'bb9_c7m12_1RB0RA_0RI0LC'
sys.path.insert(0, str(G2))
from tok2word import tok2word
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
END = (G2 / 'g2' / 'endtoks_B6.txt').read_text().strip()
m = re.match(r'^(.*) 4 2\*2 6139 1 2 (0\*6 <1 00> .*)$', END)
if not m:
    raise SystemExit('endtoks parse failed')
TAIL = m.group(2)
PFX0 = '0*2 4 9 6 210 14 10'


def build(tokens, X):
    t = re.sub(r'\bP(\d+)\b', lambda mm: PFX0 + ' 4 2 7' * int(mm.group(1)), tokens)
    return t + f' {X} ' + TAIL


def abbr(s):
    s = re.sub(r'0\*2 4 9 6 210 14 10((?: 4 2 7)*)', lambda mm: f'P{mm.group(1).count("7")}', s)
    s = re.sub(r'(0\*5 <1 00> )+', 'TAIL ', s)
    return s


if __name__ == '__main__':
    M, toks, xs, steps = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    mode = sys.argv[5] if len(sys.argv) > 5 else 'deadend'
    npr = sys.argv[6] if len(sys.argv) > 6 else '40'
    for X in xs.split(','):
        w = tok2word(build(toks, int(X)))
        print(f'## X={X} start: {abbr(build(toks, int(X)))[:200]}', flush=True)
        out = subprocess.run([str(HERE / 'tr9t.exe'), M, w, str(len(w)), 'B', steps, mode, npr], capture_output=True,
                             text=True, creationflags=LOW).stdout
        for line in out.splitlines():
            print(abbr(line)[:400], flush=True)
