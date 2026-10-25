"""logcfg.py: parse an nfol log into stage-start (J) configs: [(stage, tokens(list, farthest first, ..., a, r), far, Kdesc)]"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import expand
def configs(path):
    out = []; far = ''; kd = {}
    for line in open(path):
        m = re.match(r'(\d+) K: (.*?) \| a=(\d+) r=(\d+)(?: far=(\S+))?', line)
        if m:
            far = m.group(5) or ''; kd[int(m.group(1))] = (m.group(2), int(m.group(3)), int(m.group(4)), far); continue
        m = re.match(r'(\d+) J: ev=(\S+) zeros=(\d+) lv=\S+ -> (.*?) \| a=(\d+) r=(\d+)', line)
        if m:
            s = int(m.group(1)); toks = expand(m.group(4)) + [int(m.group(5)), int(m.group(6))]
            out.append((s, toks, far, m.group(4), m.group(2)))
    return out
