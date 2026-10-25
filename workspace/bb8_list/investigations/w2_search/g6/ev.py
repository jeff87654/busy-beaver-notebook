"""ev.py: run evtrace on a token configuration.  usage: python ev.py MACHINE "tokens farthest-first incl a r" [--far BITS] [--maxs N] [--maxev N] [--watch S] [--suf 1010] [--q G] [--state G] [--head -1]"""
import sys, subprocess, argparse, os
HERE = os.path.dirname(os.path.abspath(__file__))
def expand(s):
    v = []
    for t in s.split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        else:
            v.append(int(t))
    return v
def word_of_tokens(toks):
    return ''.join('10' * m + '1' for m in toks)
ap = argparse.ArgumentParser()
ap.add_argument('machine'); ap.add_argument('tokens')
ap.add_argument('--far', default=''); ap.add_argument('--maxs', type=int, default=2_000_000); ap.add_argument('--maxev', type=int, default=60)
ap.add_argument('--watch', default='-'); ap.add_argument('--suf', default='1010'); ap.add_argument('--q', default='G'); ap.add_argument('--state', default=None)
ap.add_argument('--head', type=int, default=-1); ap.add_argument('--E', default='1'); ap.add_argument('--raw', default=None)
a = ap.parse_args()
m = a.machine
if m.count('_') == 8: m += '_------'
word = a.raw if a.raw else a.far + word_of_tokens(expand(a.tokens)) + a.suf
head = len(word) if a.head < 0 else a.head
st = a.state or a.q
p = subprocess.run([os.path.join(HERE, 'evtrace.exe'), m, st, str(head), str(a.maxs), a.q, a.suf, a.E, str(a.maxev), a.watch], input=word, capture_output=True, text=True)
sys.stdout.write(p.stdout); sys.stderr.write(p.stderr)
