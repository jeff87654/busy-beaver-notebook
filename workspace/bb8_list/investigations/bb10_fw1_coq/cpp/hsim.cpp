// hsim: run M3 from a token configuration (far-first tokens, head in G right of the word) until halt.
// usage: hsim maxsteps tok1 tok2 ... ; tokens may be written v*count.  Prints steps, state, and a window.
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
    bool verbose = getenv("WVERB") != nullptr;
    long long maxs = atoll(argv[1]);
    std::string w;
    for (int i = 2; i < argc; ++i) {
        long long v = atoll(argv[i]), c = 1;
        const char *s = strchr(argv[i], '*'); if (s) c = atoll(s + 1);
        for (long long j = 0; j < c; ++j) { for (long long k = 0; k < v; ++k) w += "10"; w += "1"; }
    }
    long long L = w.size(), pad = 4 * L + 100000;
    std::vector<unsigned char> t(2 * pad + L, 0);
    for (long long i = 0; i < L; ++i) t[pad + i] = w[i] - '0';
    long long h = pad + L; int q = 6; long long st = 0;
    while (st < maxs) {
        int s = t[h], k = 2 * q + s;
        if (!Def[k]) break;
        if (q == 3 && (s == 0 || s == 1)) {
            static const char *pat = "111011001";
            bool ok = true;
            for (int i = 0; i < 9 && ok; ++i) ok = t[h - 9 + i] == pat[i] - '0';
            if (ok) {
                long long p = h, rho = 0;
                while (t[p] == 1 && t[p+1] == 0) { p += 2; ++rho; }
                if (t[p] == 0 && t[p+1] == 1 && t[p+2] == 0 && t[p+3] == 1) {
                    long long q2 = p + 4, n = 0;
                    while (t[q2] == 1 && t[q2+1] == 0 && t[q2+2] == 1) { q2 += 3; ++n; }
                    long long e = q2; while (e < (long long)t.size() - 8 && (t[e]|t[e+1]|t[e+2]|t[e+3]|t[e+4]|t[e+5]|t[e+6]|t[e+7])) ++e;
                    long long sp = h - 9, sb = 0;
                    while (sp >= 8 && t[sp-8]==1 && t[sp-7]==1 && t[sp-6]==1 && t[sp-5]==0 && t[sp-4]==1 && t[sp-3]==1 && t[sp-2]==1 && t[sp-1]==0) { sp -= 8; ++sb; }
                    if (verbose || rho == 0) {
                        printf("W step=%lld units=%lld zeros=%lld stack=%lld tail=", st, rho, n, sb);
                        for (long long i = q2; i < e && i < q2 + 400; ++i) putchar('0' + t[i]);
                        printf("\n");
                    }
                }
            }
        }
        t[h] = W[k]; h += Dd[k]; q = N[k]; ++st;
        if (h <= 0 || h >= (long long)t.size() - 1) { printf("WIDE\n"); return 0; }
    }
    long long lo = 0, hi = t.size() - 1;
    while (lo < h && !t[lo]) ++lo; while (hi > h && !t[hi]) --hi;
    long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += t[i];
    printf("%s steps=%lld state=%c sym=%d ones=%lld left=%lld right=%lld\n", st < maxs ? "HALT" : "LIMIT", st, 'A' + q, t[h], ones, h - lo, hi - h);
    {   // longest run of 11101110 blocks on the final tape
        long long best = 0;
        for (long long st0 = lo; st0 < lo + 8 && st0 <= hi; ++st0) {
            long long run = 0;
            for (long long p = st0; p + 8 <= hi + 1; p += 8) {
                bool m = t[p]==1&&t[p+1]==1&&t[p+2]==1&&t[p+3]==0&&t[p+4]==1&&t[p+5]==1&&t[p+6]==1&&t[p+7]==0;
                if (m) { ++run; if (run > best) best = run; } else run = 0;
            }
        }
        printf("final stack blocks=%lld\n", best);
    }
    std::string sl, sr;
    for (long long i = (h - 200 > lo ? h - 200 : lo); i < h; ++i) sl += char('0' + t[i]);
    for (long long i = h; i <= hi && i < h + 200; ++i) sr += char('0' + t[i]);
    printf("%s[%c]%s\n", sl.c_str(), 'A' + q, sr.c_str());
    return 0;
}
