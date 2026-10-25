"""Build the literal end-game configuration [A, 8, 1^z, 0, 1, 3, 0, 2, 1^2 | 1 | r] + SUF 1010 (head on blank right, state G)."""
import sys
def tok(m): return '10'*m + '1'
def word(A, r, z=3):
    toks = [A, 8] + [1]*z + [0, 1, 3, 0, 2, 1, 1] + [1, r]
    return ''.join(tok(m) for m in toks) + '1010'
if __name__ == '__main__':
    out = []
    for A in map(int, sys.argv[1].split(',')):
        for r in map(int, sys.argv[2].split(',')):
            w = word(A, r)
            out.append(f'A{A}_r{r} {w} {len(w)} G')
    print('\n'.join(out))
