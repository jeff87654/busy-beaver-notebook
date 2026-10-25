"""Helpers: reuse c7m12 word builders (read-only import)."""
import sys, subprocess, os
from pathlib import Path
C7 = Path(__file__).resolve().parent.parent / 'bb9_c7m12_1RB0RA_0RI0LC'
sys.path.insert(0, str(C7))
from dconf import build  # noqa
from inner_start import lout  # noqa
TR = str(C7 / 'tr9.exe')
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
S = 'RAW:1^8 00 1 00 1'
def K(ds, a, b):
    """champion K word, ds left-to-right (far first)"""
    return build(['RAW:11', 'D:' + ','.join(str(3 * d + 1) for d in ds + [a]), f'R:{3*b+2}', 'RAW:111001'])
def J(bo, e1, e234, a, b):
    return build([lout(bo), 'RAW:(10)^8 0', 'D:0,0,0,0', 'RAW:(10)^3 0',
                  'D:2,' + str(3 * e1 + 2) + ',' + ','.join(str(3 * e + 1) for e in e234) + f',{3 * a + 1}',
                  f'R:{3 * b + 2}', S])
def tr(m, w, maxs, mode, *args, head=None, state='B'):
    h = len(w) if head is None else head
    return subprocess.run([TR, m, w, str(h), state, str(int(maxs)), mode] + [str(x) for x in args],
                          capture_output=True, text=True, creationflags=LOW).stdout
def Kt(ds, m, r, t, pre='11'):
    """record notation: pre D(ds far->near) D(m) (10)^r 11 (11111100)^t 1001, head on blank right (state B)"""
    return pre + ''.join('10' * x + '1' for x in ds + [m]) + '10' * r + '11' + '11111100' * t + '1001'
