# consistency: oracle vs hand rules on random lists with huge tokens
import random
import rules, oracle
from num import H
random.seed(11)
agree = dis = need_both = other = 0
for trial in range(150):
    body = [random.choice([0, 1, 1, 2, 3, 4, 5, 7, 'H']) for _ in range(random.randint(1, 5))]
    t = [H(random.randint(0, 10**9))] + [H(random.randint(0, 10**9)) if v == 'H' else v for v in body] + [0, random.choice([4, 6, 16, H(random.randint(0, 10**9))])]
    try:
        e1 = rules.classify(t); r1 = ('ev', e1.newlist)
    except rules.Need: r1 = ('need',)
    except rules.Unknown: r1 = ('unk',)
    try:
        e2 = oracle.oracle_event(t); r2 = ('ev', e2.newlist)
    except rules.Need: r2 = ('need',)
    except rules.Unknown as e: r2 = ('unk', str(e))
    if r1[0] == 'ev' and r2[0] == 'ev':
        if r1[1] == r2[1]: agree += 1
        else:
            dis += 1; print('DIS', t, r1, r2)
    elif r1[0] == 'need' and r2[0] == 'need': need_both += 1
    else:
        other += 1
        if r1[0] == 'ev' or (r1[0] == 'need' and r2[0] == 'ev'): print('MIXED', t, r1[0], r2[:2] if r2[0]!='ev' else 'ev')
print('agree', agree, 'disagree', dis, 'need both', need_both, 'other', other, oracle.stats)
