from lib import word, run, M10, rle, tokens, ctok
P = [2, 1, 1, 0, 2, 1, 0, 1]
ctx = P + [44, 3, 1, 1, 0, 31, 0]
for (a, Y) in [(30, 10), (30, 40), (300, 100)]:
    toks = ctx + [a, 3, 1, 1, 0, 0, Y]
    w = word(toks)
    apos = len(word(ctx))  # index of a's first cell in w; head starts at len(w)
    print('a=%d Y=%d  (a starts %d cells left of the head)' % (a, Y, len(w) - apos))
    for n in (200, 1000, 3000, 10000, 30000, 100000, 300000):
        snaps, end = run(M10, w, 'G', '0', n)
        L = end[2]; S = end[3]; R = end[4]
        # how much of the original left part is intact
        common = 0
        while common < min(len(L), apos) and L[common] == w[common]:
            common += 1
        print('  %7d  intact-prefix %5d/%d  tapeL %d  state %s  right %s | tail %s' % (n, common, apos, len(L), S, R[:20], rle(L[apos - 5:])[:150]))
