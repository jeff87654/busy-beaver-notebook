// rec MACHINE MAXSTEPS [mode]: literal sim; print tape whenever head sets a new extreme (mode 0) ; H on halt
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
int W[16][2], D[16][2], NX[16][2];
int main(int argc, char **argv) {
    const char *p = argv[1]; int ns = 0;
    while (*p) { for (int c = 0; c < 2; ++c) { if (p[0] == '-') NX[ns][c] = -1; else { W[ns][c] = p[0]-'0'; D[ns][c] = p[1]=='R'?1:-1; NX[ns][c] = p[2]-'A'; } p += 3; } ns++; if (*p == '_') ++p; }
    long long N = atoll(argv[2]);
    const long long SZ = 1 << 22; std::vector<char> T(SZ, 0); long long h = SZ / 2, lo = h, hi = h; int q = 0;
    long long nprint = 0, maxp = argc > 3 ? atoll(argv[3]) : 200;
    for (long long st = 0; st < N; ++st) {
        int c = T[h];
        if (NX[q][c] < 0) {
            long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += T[i];
            printf("H %lld ones=%lld span=%lld state=%c\n", st, ones, hi - lo + 1, 'A' + q);
            std::string s; for (long long i = lo; i <= hi; ++i) s += (i == h ? (T[i] ? 'I' : 'O') : (T[i] ? '1' : '0'));
            printf("  %s\n", s.c_str()); return 0;
        }
        T[h] = W[q][c]; h += D[q][c]; q = NX[q][c];
        if (argc > 4) { // mode: print when head arrives at an edge (side argv[4]: R or L) in state argv[5]
            bool atR = argv[4][0] == 'R';
            bool ev = atR ? (h >= hi) : (h <= lo);
            if (h < lo) lo = h; if (h > hi) hi = h;
            if (ev && (argv[5][0] == '*' || argv[5][0] == 'A' + q) && st + 1 >= atoll(argv[6]) && nprint++ < maxp) {
                std::string s; for (long long i = lo; i <= hi; ++i) s += (i == h ? (T[i] ? 'I' : 'O') : (T[i] ? '1' : '0'));
                printf("%lld %c %s\n", st + 1, 'A' + q, s.c_str());
            }
            continue;
        }
        if (h < lo || h > hi) {
            if (h < lo) lo = h; else hi = h;
            if (nprint++ < maxp) {
                std::string s; for (long long i = lo; i <= hi; ++i) s += (i == h ? (T[i] ? 'I' : 'O') : (T[i] ? '1' : '0'));
                printf("%lld %c %s\n", st + 1, 'A' + q, s.c_str());
            }
        }
        if (h < 2 || h > SZ - 3) { printf("TAPE\n"); return 0; }
    }
    printf("END %lld span=%lld\n", N, hi - lo + 1);
}
