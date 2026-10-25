"""Check the K-family rules of the mirror machine against exact literal simulation, including b=0 and k>=b."""
import os, sys, itertools
os.environ['BB_KENC'] = '10,0'
from kfam import run_next, set_shape, show, trailing_zeros, strip
set_shape('E', '11')
TM = '1LB0LA_0LC0LD_0RD---_1LE0RF_1LF1LD_1RE0RG_1RF1RH_0LA0RG'

def predict(ds, a, b):
    ds = list(ds)
    if a >= 1:
        if not ds and a == 1:
            return predict(ds, 0, b + 2)
        return ('K', (tuple(ds), a - 1, b + 2))
    k = trailing_zeros(ds)
    if k == len(ds):
        if b < 1: return None
        return ('K', (strip((2,) + (1,) * (b - 1)), 1, 0))
    i = len(ds) - 1 - k
    if k == 0:
        if b == 0:
            return ('HALT',)
        ds[-1] -= 1
        return ('K', (strip(ds), b + 2, 0))
    if k < b:
        ds[i] -= 1
        ds = ds[:i + 1] + [b + 2 - k] + [1] * (k - 1)
        return ('K', (strip(ds), 1, 0))
    if k == b:
        return ('HALT',)
    return None

def kind(ds, a, b):
    if a >= 1: return 'R1'
    k = trailing_zeros(ds)
    if k == len(ds): return 'R4'
    if k == 0: return 'R2'
    return 'R3' if k < b else ('HALT' if k == b else 'R3big')

