"""Orbits of the proved recurrences (main machine and F0 variant), with magnitudes.
Only exact values up to ~10^10000 are built; beyond that the orbit is described in closed form.

Main:    Fa(m,q+1,t) -> Fa(2m+1,q,t); Fa(m,0,4) -> Fb(2m+1); Fa(m,0,0) -> Fa(0,4m+1,4); Fb(m) -> Fa(0,4m+1,0).
         q rounds at once: Fa(m,q,t) -> Fa((m+1)2^q - 1, 0, t).  Hence Fa(0,q,0) -> Fa(0, 2^(2^(q+2)) - 3, 0).
Variant: VF(m,q+1,t) -> VF(2m+1,q,t); VF(m,0,11) -> VF(0,4m+1,111); VF(m,0,111) -> VF(0,4m+1,11w);
         VF(m,0,11w) -> VF(0,4m+1,1111w); VF(m,0,1111w) -> VF(0,8m+5,1); VF(m,0,1) -> VF(0,4m+2,1).
"""
import math
import sys
sys.set_int_max_str_digits(100000)

LOG2 = math.log10(2)


def n(x):
    return str(x) if x < 10**15 else '~10^%.4f' % (len(str(x)) - 1 + math.log10(int(str(x)[:15]) / 10**14))


print('Main machine, from Fa(0,1,1111) (step 115); "q rounds" collapsed:')
m, q, t = 0, 1, 4
for _ in range(8):
    print('   Fa(%s, %s, %s)' % (n(m), n(q), '1111' if t else 'empty'))
    if q > 40000:
        lq = len(str(q)) - 1 + math.log10(int(str(q)[:15]) / 10**14)
        print('   ... next: Fa(2^q - 1, 0, %s) with q above, i.e. m ~ 10^(10^%.4f)' % ('1111' if t else 'empty', lq + math.log10(LOG2)))
        break
    if q > 0:
        m, q = (m + 1) * 2**q - 1, 0
        continue
    if t == 4:
        mb = 2 * m + 1
        print('   Fb(%s)' % n(mb))
        m, q, t = 0, 4 * mb + 1, 0
    else:
        m, q, t = 0, 4 * m + 1, 4
print('   Fa(0,q,empty) -> Fa(0, 2^(2^(q+2)) - 3, empty): q = 13, 2^32768 - 3 (~10^%.3f), 2^(2^(2^32768-1)) - 3, ...'
      % (32768 * LOG2))
print('   ones on the tape at Fa(0,q,t) ~ 5q + small, e.g. ~10^%.2f at the start of the 4th phase'
      % (math.log10(5) + 32768 * LOG2))

print('Variant, from VF(0,1,11) (step 109):')
print('   VF(0,1,11) -> VF(1,0,11) -> VF(0,5,111) -> VF(31,0,111) -> VF(0,125,11w) -> VF(2^125-1,0,11w)')
print('   -> VF(0,2^127-3,1111w) -> VF(2^(2^127-3)-1,0,1111w) -> VF(0,2^(2^127)-3,1), then VF(0,q,1) -> VF(0,2^(q+2)-2,1)')
print('   2^125-1 = %d, 2^127-3 = %d' % (2**125 - 1, 2**127 - 3))
