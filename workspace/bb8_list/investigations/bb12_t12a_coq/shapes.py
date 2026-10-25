"""Symbolic shapes for n1 B-forms: tokens left-to-right, head in H on the blank right of the word."""
from common import *
def H(left): return ('H', list(left), [BLANK], '>')
def W(*toks, far=None):
    """toks: token streams, left-to-right; far: the side left of them (default: blank)"""
    left = []
    for t in reversed(toks): left += t
    return H(left + (far if far is not None else [BLANK]))
def ONES(**v): return [run((1, 0, 1), **v)]          # D1^v
def TWOS(**v): return [run((1, 0, 1, 0, 1), **v)]    # D2^v
def T3(c, **v):
    """token D(c + 3*v) with the variable part as (01)^3 blocks"""
    return [1] + [0, 1] * c + [run((0, 1) * 3, **v)]
def Z(): return tok(0)
