"""probe.py MACHINE "RLE word" STATE MAXSTEPS SIDE ESTATE [MAXLINES] [MODE]
Expand an RLE word like "(10)^3 (01)^2 000 (10)^5 1" (tokens: bits, or (xy)^k, or b^k) and run ksnap.exe from it
with the head on the blank cell right of the word (append '<' to the word spec to put it left of the word instead)."""
import re, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
def expand(s):
    out = []
    for tok in s.split():
        m = re.fullmatch(r'\((\d+)\)\^(\d+)', tok)
        if m: out.append(m.group(1) * int(m.group(2))); continue
        m = re.fullmatch(r'([01])\^(\d+)', tok)
        if m: out.append(m.group(1) * int(m.group(2))); continue
        assert re.fullmatch(r'[01]+', tok), tok
        out.append(tok)
    return ''.join(out)
m, spec, st, mx, side, est = sys.argv[1:7]
rest = sys.argv[7:]
left = spec.endswith('<')
w = expand(spec.rstrip('<'))
if left:
    w = '0' + w; head = 0
else:
    w = w + '0'; head = len(w) - 1
sys.exit(subprocess.call([os.path.join(HERE, 'ksnap.exe'), m, w, str(head), st, mx, side, est] + rest, creationflags=0x40))
