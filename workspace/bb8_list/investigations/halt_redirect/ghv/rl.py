import sys, re
def comp(s):
    # compress (10)^k runs (k>=3) and 1^k / 0^k runs
    return re.sub(r'(?:10){3,}', lambda m: f'(10)^{len(m.group(0))//2} ', s)
for l in sys.stdin:
    a, _, b = l.partition(': ')
    print(a + ': ' + comp(b.strip()))
