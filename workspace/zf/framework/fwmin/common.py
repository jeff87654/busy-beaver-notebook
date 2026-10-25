"""Shared helpers for fwmin: import Wade's builder/program from ext (read-only)."""
import sys, os
EXT = r'C:\Users\jeffr\Downloads\bb8\zf\ext\turing_machine_explorer'
HERE = os.path.dirname(os.path.abspath(__file__))
if EXT not in sys.path: sys.path.insert(0, EXT)
import tm, TMBuilder, zf2
AXIOMORDER = [16, 17, 3, 18, 4, 7, 8, 9, 11, 5, 12, 13, 14, 2, 15, 0, 1, 6, 10, 19]

def count(t):
    names = set(s for (s, _) in t.states)
    fw = sorted(s for s in names if s[0].isdigit())
    return len(fw), len(names) - len(fw), len(names), fw
