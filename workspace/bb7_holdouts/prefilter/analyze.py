import sys, collections
def load_pf(f):
    rows = {}
    hdr = None
    for l in open(f):
        if l.startswith('#'): continue
        x = l.rstrip('\n').split('\t')
        if x[0] == 'machine': hdr = x; continue
        rows[x[0]] = dict(zip(hdr, x))
    return rows
def load_dl2(f):
    g = {}
    for l in open(f):
        if l.startswith(('#', 'machine')): continue
        x = l.rstrip('\n').split('\t'); g[x[0]] = (x[3], x[4])
    return g
