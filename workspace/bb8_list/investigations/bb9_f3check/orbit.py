# my own orbit / class model (sketch convention L; D0f P convention, see wsim --d0)
C = {0: -100, 1: 32, 2: -46, 3: -64, 4: -52}
CONS = {0: 3, 1: 11, 2: 4, 3: 6, 4: 6}
def g(L): return (3 * L + C[L % 5]) // 5
def classify(L0first, P0):
    """L0first = sketch L at the first D0 moment, P0 = D0 P there. returns (key, rho, orbit)"""
    L, P, orb = L0first, P0, [L0first]
    while L >= 60:
        P -= CONS[L % 5]
        L = g(L); orb.append(L)
    rho = (P - 35) % 5 if L == 31 else None
    return L, rho, P, orb
if __name__ == "__main__":
    import sys
    print(classify(int(sys.argv[1]), int(sys.argv[2])))
