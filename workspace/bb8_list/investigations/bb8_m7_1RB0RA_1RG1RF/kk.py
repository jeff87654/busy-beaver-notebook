import sys
sys.path.insert(0,'.')
import planner8 as pl
from planner8 import *
def run(cnt,blk=(1,0)): return ('run',tuple(blk),lin({cnt:1}))
def U(c=0, v=None, coef=1):
    """c units + coef*v units of (01), nearest-first stream"""
    t=[1,0]*c
    if v: t.append(('run',(1,0),lin({v:coef})))
    return t
def Kleft(digits, a, b, tail=None, end=None):
    """digits: list of (c,v) nearest first; a,b: (c,v) unit counts (already 3x+1 forms by caller); tail (c,v)"""
    tail = tail or (2,None)
    t=U(*tail)+[1]+U(*b)+[1]+U(*a)+[1]
    for d in digits:
        t+=U(*d)+[1]
    return t+(end if end is not None else [BLANK])
