# residue of power towers mod m, exact (handles small exponents)
from sympy import totient
import sys
sys.setrecursionlimit(10000)
BIG=10**6
def tower_val_capped(h, top):
    # returns min(actual, BIG) of 2^^h top  (h twos then top)
    v=top
    for _ in range(h):
        if v>=64: return BIG
        v=2**v
        if v>=BIG: return BIG
    return v
def tmod(h, top, m):
    # (2^2^...^top) with h twos, mod m
    if m==1: return 0
    if h==0: return top % m
    e_small = tower_val_capped(h-1, top)
    if e_small < BIG: return pow(2, e_small, m)
    ph=int(totient(m))
    e = tmod(h-1, top, ph)
    # use generalized Euler: 2^e mod m = 2^(e mod ph + ph) when e>=log2 m
    return pow(2, e % ph + ph, m)
if __name__=="__main__":
    for M in [5040, 7200, 2*2520*7200]:
        for h in [5,8,13,20]:
            print(M,h,tmod(h,3,M), tmod(h,4,M), tmod(h,16,M))
