"""Expected word at the start of the inner counter after the outer exhaustion K(0^11; 0; b):
L(b) = 11 D(7) D(1)^(12b-2) D(0) (10)^8 0 1111 (10)^3 0, inner list D(2) D(5) D(4)^4, b-run (10)^8, suffix S'.
  python inner_start.py B [INNER_TOKENS=2,5,4,4,4,4] [YRUN=8]"""
import sys

sys.path.insert(0, '.')
from dconf import build  # noqa: E402


def lout(b):
    return 'D:0,0,7,' + ','.join(['1'] * (12 * b - 2)) + ',0'


def inner_word(b, toks='2,5,4,4,4,4', y=8):
    return build([lout(b), 'RAW:(10)^8 0', 'D:0,0,0,0', 'RAW:(10)^3 0', 'D:' + toks, f'R:{y}', 'RAW:1^8 00 1 00 1'])


if __name__ == '__main__':
    b = int(sys.argv[1])
    toks = sys.argv[2] if len(sys.argv) > 2 else '2,5,4,4,4,4'
    y = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    print(inner_word(b, toks, y))
