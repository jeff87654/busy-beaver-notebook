"""ev13.py: run evtrace13 on a token configuration (GH family defaults).
usage: python ev13.py MACHINE "tokens farthest-first incl a r" [--far BITS] [--maxs N] [--maxev N] [--watch IJK] [--win 30]"""
import sys, subprocess, argparse, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from g6lib import expand, word_of_tokens
ap = argparse.ArgumentParser()
ap.add_argument('machine'); ap.add_argument('tokens')
ap.add_argument('--far', default=''); ap.add_argument('--maxs', type=int, default=200_000_000); ap.add_argument('--maxev', type=int, default=60)
ap.add_argument('--watch', default='-'); ap.add_argument('--suf', default='1010'); ap.add_argument('--q', default='G')
ap.add_argument('--win', default='30')
a = ap.parse_args()
word = a.far + word_of_tokens(expand(a.tokens)) + a.suf
p = subprocess.run([os.path.join(HERE, 'evtrace13.exe'), a.machine, a.q, str(len(word)), str(a.maxs), a.q, a.suf, '1', str(a.maxev), a.watch, a.win], input=word, capture_output=True, text=True)
sys.stdout.write(p.stdout); sys.stderr.write(p.stderr)
