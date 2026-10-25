"""per.py: classify follower histories: find Per-like K-moments [.. 2^x 5 1^m 0^{2,3} ..] and report the counter m per stage."""
import re
def per_m(tokens):
    """tokens = digits (farthest first) + [a, r]; returns list of (x, m, zeros) for every '2^x 5 1^m 0' pattern"""
    t = tokens[:-2]; out = []
    i = 0
    nz = 0
    for v in t[::-1]:
        if v != 1: break
        nz += 1
    while i < len(t):
        if t[i] == 2:
            j = i
            while j < len(t) and t[j] == 2: j += 1
            if j < len(t) and t[j] == 5:
                k = j + 1
                while k < len(t) and t[k] == 1: k += 1
                if k < len(t) and t[k] == 0:
                    out.append((j - i, k - j - 1, nz))
            i = j if j > i else i + 1
        else:
            i += 1
    return out
