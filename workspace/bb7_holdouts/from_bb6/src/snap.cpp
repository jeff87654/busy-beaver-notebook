// snap MACHINE T1 T2 ... : run from blank, print "W snap<t> tape pos state" at each listed step (must be increasing)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
int nx[8][2], wr[8][2], dr[8][2];
int main(int argc, char **argv) {
    const char *s = argv[1]; int len = strlen(s), q = 0;
    for (int i = 0; i < len; i += 7, ++q) for (int c = 0; c < 2; ++c) { const char *x = s + i + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') nx[q][c] = -1; else { wr[q][c] = x[0] - '0'; dr[q][c] = x[1] == 'R' ? 1 : -1; nx[q][c] = x[2] - 'A'; } }
    long long SZ = 1LL << 26; std::vector<unsigned char> T(SZ, 0); long long p = SZ / 2, lo = p, hi = p, t = 0; int qq = 0;
    for (int k = 2; k < argc; ++k) { long long tt = atoll(argv[k]);
        while (t < tt) { int c = T[p]; if (nx[qq][c] < 0) { fprintf(stderr, "halted at %lld\n", t); return 0; }
            T[p] = wr[qq][c]; p += dr[qq][c]; qq = nx[qq][c]; ++t; if (p < lo) lo = p; if (p > hi) hi = p; }
        printf("W snap%lld ", t); for (long long i = lo - 1; i <= hi + 1; ++i) putchar('0' + T[i]); printf(" %lld %c\n", p - lo + 1, 'A' + qq); }
}
