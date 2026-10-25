"""K-family words.  K(ds; a; b) = 11 D(3d+1).. D(3a+1) (10)^(3b+2) 111001, head in B on the blank to the right."""
import sys
def D(m): return '10' * m + '1'
def K(ds, a, b, tail='111001'):
    return '11' + ''.join(D(3 * d + 1) for d in ds) + D(3 * a + 1) + '10' * (3 * b + 2) + tail
def T(toks, r, tail='111001'):
    """raw tokens (D-lengths, farthest first, a-token last), accumulator run r"""
    return '11' + ''.join(D(m) for m in toks) + '10' * r + tail
if __name__ == '__main__':
    n, b = int(sys.argv[1]), int(sys.argv[2])
    print(K([0] * n, 0, b))
