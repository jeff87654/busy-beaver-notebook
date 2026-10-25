"""Negative control for check_R.py: run it with deliberately wrong predictions (O result length, Z0 step count,
C2 with r placed one cell off, D reading one cell less) and confirm that every one is reported as FAIL."""
import sys, io, contextlib
src = open('check_R.py').read()
bad = src.replace("lambda p: o(2*p+5), False", "lambda p: o(2*p+7), False") \
         .replace("True, lambda q: 24*q + 5)", "True, lambda q: 24*q + 6)") \
         .replace("lambda p: o(8*p+27), False", "lambda p: o(8*p+26), False") \
         .replace("lambda p: o(2*p) + '0010', lambda p: '1' + z(2*p-1) + o(6)", "lambda p: o(2*p) + '001', lambda p: '1' + z(2*p-1) + o(5)")
assert bad.count('o(2*p+7)') == 1 and bad.count('24*q + 6') == 1 and bad.count('o(8*p+26)') == 1
sys.argv = ['check_R.py', 'R1', '--pmax', '6', '--qmax', '4', '--qmaxZZ', '1', '--tails', '2']
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(compile(bad, 'check_R_bad', 'exec'))
out = buf.getvalue()
print(out)
for name in ('O ', 'D ', 'C2', 'Z0'):
    line = [l for l in out.splitlines() if l.startswith(name.ljust(4)) or l.startswith(name + ' ')][0]
    print('negative control', name.strip(), 'detected' if ' 0 ok ' in line or 'fail' in line and not ' 0 fail' in line else 'NOT DETECTED')
