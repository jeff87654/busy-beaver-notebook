"""Construction word of the champion-template configuration K(ds; a; b) (head just right of it, state B)."""
import sys


def kword(ds, a, b):
    s = '11'
    for d in ds:
        s += '10' * (3 * d + 1) + '1'
    s += '10' * (3 * a + 1) + '1' + '10' * (3 * b + 2) + '111001'
    return s


if __name__ == '__main__':
    n, a, b = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    lead = [int(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else []
    print(kword(lead + [0] * n, a, b))
