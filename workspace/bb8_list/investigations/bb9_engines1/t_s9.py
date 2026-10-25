"""ordered-representative follow from a hand-built stage configuration: list tokens (farthest first) + SUF"""
import sys, threading
sys.setrecursionlimit(30000); threading.stack_size(64*1024*1024)
import fam, mfx, mf35
BASES = {l.split()[0]: l.split()[1:] for l in open('bases.txt') if l.strip() and not l.startswith('#')}
lbl, m = sys.argv[1], sys.argv[2]; toks = eval(sys.argv[3]); st = int(sys.argv[4]); M = int(sys.argv[5]); maxs = int(float(sys.argv[6]))
ordered = sys.argv[7] == 'o' if len(sys.argv) > 7 else True
base, t, n = BASES[lbl]; F = fam.register(lbl, base, t, int(n))
word = mf35.word_of_tokens(toks) + F['SUF']
m10 = m + '_------' * (9 - m.count('_'))
def main():
    k, h = mfx.follow(lbl, m10, st, maxs, 0, M, 19, ordered=ordered, verbose=True, start=(word, len(word), F['Q']), gtop0=max(toks))
    print('RESULT', k, h[-1])
th = threading.Thread(target=main); th.start(); th.join()
