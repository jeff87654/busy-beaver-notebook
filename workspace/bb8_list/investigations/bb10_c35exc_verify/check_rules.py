"""check_rules.py -- verify rules.classify against literal B-form events of sim.exe on random configurations.
usage: check_rules.py SEED NTRIALS [profile]"""
import random, sys, time
from collections import Counter
from lib import bforms, ctok, M10
import rules
from num import mod3

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
NT = int(sys.argv[2]) if len(sys.argv) > 2 else 300
prof = sys.argv[3] if len(sys.argv) > 3 else 'mix'
random.seed(seed)
P = [2, 1, 1, 0, 2, 1, 0, 1]
stats = Counter(); unk = Counter(); bad = 0; t0 = time.time()


def rand_body():
    if prof == 'ones':
        out = []
        for _ in range(random.randint(1, 5)):
            out += [random.choice([0, 2, 3, 4, 5, 6, 7, 9, 12])] + [1] * random.choice([0, 0, 1, 2, 3])
        return out
    return [random.choice([0, 1, 1, 1, 2, 3, 3, 4, 5, 6, 7, 8, 9]) for _ in range(random.randint(1, 6))]


for trial in range(NT):
    toks = P + [random.randint(12, 40)] + rand_body() + [0, random.randint(2, 14)]
    bf, end = bforms(M10, toks, 4 * 10**6, maxsnap=40)
    lits = [b[1] for b in bf[1:]]
    t = list(toks)
    pos = 0
    while pos < len(lits):
        try:
            ev = rules.classify(t)
        except rules.Unknown as e:
            unk[str(e)] += 1
            break
        nsteps = 1
        if ev.name == 'R1*':
            x = t[ev.lo]
            nsteps = (x - {1: 1, 0: 0, 2: 2}[x % 3]) // 3
        if pos + nsteps - 1 >= len(lits):
            break
        lit = lits[pos + nsteps - 1]
        if ev.newlist != lit:
            bad += 1
            if bad <= 15:
                print('MISMATCH', ev.name, 'from', ctok(t), '\n   rule', ctok(ev.newlist), '\n   lit ', ctok(lit))
            break
        stats[ev.name] += 1
        t = ev.newlist
        pos += nsteps
print('profile', prof, 'seed', seed, 'trials', NT)
print('rules verified:', dict(stats))
print('unknown patterns:', sorted(unk.items(), key=lambda a: -a[1]))
print('mismatches', bad, 'time %.1f' % (time.time() - t0))
