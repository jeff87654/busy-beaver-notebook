"""geneval.py: 2-adic evaluator for digit-list (Ackermann) K-dynamics.
Rules (digits counted from the right, position 1 = last digit):
  D   [.., d+1; a] -> [.., d; al*a + be]
  Bk  [.., y+1, 0^k; a] -> [.., y, ga*a + de + ep*k, t^(k-1); a0]
h_1(x) = al*x+be ; h_i(x) = h_{i-1}^{R_i(x)}( c_{i-2} ),  R_i(x) = ga*x+de+ep*(i-1),
c_0 = a0, c_m = h_m^t(c_{m-1}).  A list [v_n..v_1] from a ends (all zero) with h_n^{v_n}(...h_1^{v_1}(a)).
Everything mod M = 2^N.  Assumption (true in real runs): the iteration count R_i(x) for i >= 3 is huge (>= orbit tail),
and orbit cycle lengths divide M (checked).  Values: exact ints when small, else residues ('huge')."""
class Huge:
    def __init__(s, r): s.r = r
    def __repr__(s): return f'H({s.r})'
class Eng:
    def __init__(s, al, be, ga, de, ep, t, a0, N=10):
        s.al, s.be, s.ga, s.de, s.ep, s.t, s.a0, s.M = al, be, ga, de, ep, t, a0, 1 << N
        M = s.M
        s.h = {1: tuple((al * x + be) % M for x in range(M))}
        s.c = {0: a0 % M}
    def orbit(s, f, x):
        seen, seq = {}, []
        while x not in seen: seen[x] = len(seq); seq.append(x); x = f[x]
        mu = seen[x]; lam = len(seq) - mu
        assert s.M % lam == 0, f'cycle length {lam} does not divide M'
        return seq, mu, lam
    def itr(s, f, x, n):
        """f^n(x), n exact int or Huge (assumed >= tail)."""
        if isinstance(n, int) and n < 4 * s.M:
            for _ in range(n): x = f[x]
            return x
        seq, mu, lam = s.orbit(f, x)
        r = n.r if isinstance(n, Huge) else n
        return seq[mu + ((r - mu) % lam)]
    def H(s, i):
        if i in s.h: return s.h[i]
        hp = s.H(i - 1); c = s.C(i - 2); M = s.M
        tab = []
        for x in range(M):
            R = (s.ga * x + s.de + s.ep * (i - 1)) % M
            tab.append(s.itr(hp, c, Huge(R) if i >= 3 else R + M * 4))   # i=2: h_1 is a permutation when al odd
        s.h[i] = tuple(tab); return s.h[i]
    def C(s, m):
        if m in s.c: return s.c[m]
        s.c[m] = s.itr(s.H(m), s.C(m - 1), s.t); return s.c[m]
    def period(s, maxi=4000):
        """find i0, P with (h_i, c_{i-1}, i mod M if ep) periodic for i >= i0."""
        seen = {}
        for i in range(2, maxi):
            key = (s.H(i), s.C(i - 1), (i % s.M) if s.ep else 0)
            if key in seen: return seen[key], i - seen[key]
            seen[key] = i
        raise RuntimeError('no period')
    def Hbig(s, i):
        """h_i for i exact int or Huge (residue of i mod M)."""
        if isinstance(i, int): return s.H(i)
        i0, P = s.period(); assert s.M % P == 0
        j = i0 + ((i.r - i0) % P); return s.H(j)
    def run_list(s, runs, a):
        """runs = [(value, count)] from the FIRST digit to the last; value exact int or Huge; count exact or Huge.
        returns a mod M after processing the whole list to zeros (lowest positions first)."""
        x = a % s.M if isinstance(a, int) else a.r
        pos = 0
        for val, cnt in reversed(runs):
            if isinstance(cnt, int):
                for _ in range(cnt):
                    pos += 1; x = s.itr(s.H(pos), x, val)
            else:
                # Huge run of equal digits: positions pos+1 .. pos+cnt; needs periodic regime
                i0, P = s.period(); assert s.M % P == 0
                # iterate exactly until periodic, then use periodicity of the composite map over one period
                # composite over positions: x -> h_{pos+cnt}^val(...h_{pos+1}^val(x)); treat as table iteration
                start = pos + 1
                k = 0
                while start + k < i0 + 2 * P and k < 10 ** 6:
                    x = s.itr(s.H(start + k), x, val); k += 1
                # now positions are periodic with period P: compose one period as a table
                base = start + k
                tab = list(range(s.M))
                for j in range(P):
                    hj = s.H(base + j); tab = [s.itr(hj, y, val) for y in tab]
                rem = (cnt.r - k) % s.M  # remaining count residue
                # rem = q*P + r : apply composite q times then r singles; q huge -> orbit
                r = rem % P; q = (rem - r) // P   # q known mod M/P
                x = s.itr(tuple(tab), x, Huge(q % (s.M // P)) if True else q)
                for j in range(r): x = s.itr(s.H(base + j), x, val)
                pos = None   # position no longer exact; only valid if this is the last run (first digits)
                pos_res = (base + r)
                s._posres = pos_res
        return x
