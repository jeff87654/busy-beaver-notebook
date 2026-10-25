#include <cstdio>
#include <cstdlib>
#include <vector>
int W[16][2], D[16][2], NX[16][2];
int main(int argc, char **argv) {
    const char *p = argv[1]; int ns = 0;
    while (*p) { for (int c = 0; c < 2; ++c) { if (p[0] == '-') NX[ns][c] = -1; else { W[ns][c] = p[0]-'0'; D[ns][c] = p[1]=='R'?1:-1; NX[ns][c] = p[2]-'A'; } p += 3; } ns++; if (*p == '_') ++p; }
    long long N = atoll(argv[2]);
    const long long SZ = 1 << 24; std::vector<unsigned char> T(SZ, 0); long long h = SZ / 2, lo = h, hi = h; int q = 0;
    long long st = 0;
    for (; st < N; ++st) {
        int c = T[h];
        if (NX[q][c] < 0) { long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += T[i];
            printf("%s H steps=%lld ones=%lld span=%lld\n", argv[1], st, ones, hi - lo + 1); return 0; }
        T[h] = W[q][c]; h += D[q][c]; q = NX[q][c];
        if (h < lo) lo = h; if (h > hi) hi = h;
        if (h < 2 || h > SZ - 3) { printf("%s TAPE %lld\n", argv[1], st); return 0; }
    }
    printf("%s END steps=%lld span=%lld\n", argv[1], st, hi - lo + 1);
}
