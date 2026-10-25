// tdump: run from token config; between steps S0 and S1, every K steps print the tape as tokens with the head marked.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
static const char *M = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA";
int W[20], Dd[20], N[20]; bool Def[20];
int main(int argc, char **argv) {
    for (int q = 0; q < 10; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = M + 7 * q + 3 * c;
        if (x[0] == '-') { Def[2*q+c] = false; continue; }
        Def[2*q+c] = true; W[2*q+c] = x[0]-'0'; Dd[2*q+c] = x[1]=='R'?1:-1; N[2*q+c] = x[2]-'A';
    }
    long long S0 = atoll(argv[1]), S1 = atoll(argv[2]), K = atoll(argv[3]);
    std::string w;
    for (int i = 4; i < argc; ++i) {
        long long v = atoll(argv[i]), c = 1;
        const char *s = strchr(argv[i], '*'); if (s) c = atoll(s + 1);
        for (long long j = 0; j < c; ++j) { for (long long k = 0; k < v; ++k) w += "10"; w += "1"; }
    }
    long long L = w.size(), pad = 4 * L + 100000;
    std::vector<unsigned char> t(2 * pad + L, 0);
    for (long long i = 0; i < L; ++i) t[pad + i] = w[i] - '0';
    long long h = pad + L; int q = 6; long long st = 0;
    while (st <= S1) {
        if (st >= S0 && (st - S0) % K == 0) {
            long long lo = 0; while (!t[lo]) ++lo; long long hi = t.size() - 1; while (!t[hi]) --hi;
            if (h > hi) hi = h;
            printf("%lld:", st);
            long long i = lo;
            while (i <= hi) {
                if (i == h) printf(" [%c]", 'A' + q);
                if (t[i] == 1) { long long j = i, m = 0; while (j + 2 <= hi && t[j+1] == 0 && t[j+2] == 1 && j + 1 != h && j + 2 != h) { j += 2; ++m; } printf(" %lld", m); i = j + 1; }
                else { printf(" _"); ++i; }
            }
            printf("\n");
        }
        int s = t[h], k = 2 * q + s;
        if (!Def[k]) break;
        t[h] = W[k]; h += Dd[k]; q = N[k]; ++st;
    }
    return 0;
}
