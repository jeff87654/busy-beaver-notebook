import sys
def kspec(n, b):
    # K0(n,b) = 11 (101)^(n+1) (10)^(3b+2) 111001  as run spec
    return '11' + '101'*(n+1) + '10'*(3*b+2) + '111001'
def runspec_of_word(w):
    w = w.rstrip('0'); out = []; i = 0
    while i < len(w):
        j = i
        while j < len(w) and w[j] == '1': j += 1
        k = j
        while k < len(w) and w[k] == '0': k += 1
        z = k - j; o = j - i
        out.append(f"{o}" if z == 1 else (f"{o}." if z == 0 else (f"{o}|" if z == 2 else f"{o}|{z}|")))
        i = k
    return ' '.join(out)
if __name__ == '__main__':
    print(runspec_of_word(kspec(int(sys.argv[1]), int(sys.argv[2]))))
