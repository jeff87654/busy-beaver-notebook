"""kg.py: k-gram context sets of literal stages (kgram.exe). Library + CLI.
kgrams(machine, tokens, far='', kmax=5, maxs=..., rcap=600) -> (end, {(k, tuple): (count, firststep)})"""
import sys, subprocess, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from g6lib import expand, word_of_tokens
def kgrams(machine, tokens, far='', kmax=5, maxs=3_000_000_000, rcap=600):
    word = far + word_of_tokens(expand(tokens) if isinstance(tokens, str) else tokens) + '1010'
    p = subprocess.run([os.path.join(HERE, 'kgram.exe'), machine, 'G', str(len(word)), str(maxs), 'G', '1010', '1', str(kmax), str(rcap)],
                       input=word, capture_output=True, text=True, creationflags=getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0))
    lines = p.stdout.splitlines(); end = lines[0]
    d = {}
    for l in lines[1:]:
        _, k, g, c, f = l.split()
        d[(int(k), tuple(g.split(',')))] = (int(c), int(f))
    return end, d
