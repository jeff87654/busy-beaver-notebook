"""egrid.py MACHINE AMAX BLIST [STEPS]: probe the empty-list configuration K(;a;b) and report the first family config with a
nonempty list (or halt). Prints a table a x b."""
import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
if __name__ == '__main__':
    M = sys.argv[1]; AM = int(sys.argv[2]); BL = [int(x) for x in sys.argv[3].split(',')]; ST = int(sys.argv[4]) if len(sys.argv) > 4 else 10**8
    pre = [int(x) for x in sys.argv[5].split(',')] if len(sys.argv) > 5 and sys.argv[5] else []
def short(ds):
    out, i = [], 0
    while i < len(ds):
        j = i
        while j < len(ds) and ds[j] == ds[i]: j += 1
        out.append(f'{ds[i]}^{j-i}' if j - i > 1 else str(ds[i])); i = j
    return ','.join(out)
for a in range(AM + 1) if __name__ == "__main__" else []:
    row = []
    for b in BL:
        ev = kl.run(M, pre, a, b, ST, 0, 400)
        r = 'T'
        for e in ev[1:]:
            if e[0] == 'H': r = f'H@{e[1]}{e[2]}{e[3]}'; break
            if e[0] == 'K' and e[2] != pre: r = f'[{short(e[2])};{e[3]};{e[4]}]'; break
        row.append(r)
    print(a, ' | '.join(row), flush=True)
