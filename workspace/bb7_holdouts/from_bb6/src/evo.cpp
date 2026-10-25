// evo N K < machines : K log-spaced snapshots from N/1000 to N; per snapshot "t:span:nblk:e1/e2/e3/e4" (nblk = blocks with
// >=3 reps of a period-1..4 unit; e_i = largest block lengths in cells); line per machine.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <vector>
#include <string>
#include <algorithm>
int nx[8][2], wr[8][2], dr[8][2], NS;
static void parse(const char *s) { int len = strlen(s), q = 0;
    for (int i = 0; i < len && q < 8; i += 7, ++q) for (int c = 0; c < 2; ++c) { const char *x = s + i + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') nx[q][c] = -1; else { wr[q][c] = x[0] - '0'; dr[q][c] = x[1] == 'R' ? 1 : -1; nx[q][c] = x[2] - 'A'; } } NS = q; }
int main(int argc, char **argv) {
    long long N = atoll(argv[1]); int K = atoi(argv[2]); long long SZ = 1LL << 26; std::vector<unsigned char> T(SZ, 0);
    char buf[256];
    while (scanf("%255s", buf) == 1) {
        parse(buf); long long p = SZ / 2, lo = p, hi = p, t = 0; int q = 0; std::string out; bool dead = false;
        for (int k = 0; k < K && !dead; ++k) {
            long long tt = (long long)(N / 1000.0 * pow(1000.0, k / (double)(K - 1)));
            while (t < tt) { int c = T[p]; if (nx[q][c] < 0) { dead = true; out += " HALT"; break; }
                T[p] = wr[q][c]; p += dr[q][c]; q = nx[q][c]; ++t; if (p < lo) lo = p; if (p > hi) hi = p;
                if (p <= 1 || p >= SZ - 2) { dead = true; out += " OOB"; break; } }
            if (dead) break;
            std::vector<long long> bl; long long i = lo;
            while (i <= hi) { long long best = 0; int bp = 0;
                for (int pp = 1; pp <= 4; ++pp) { long long j = i + pp; while (j <= hi && T[j] == T[j - pp]) ++j; long long L = j - i, r = L / pp;
                    if (r >= 3 && r * pp > best) { best = r * pp; bp = pp; } }
                if (bp) { bool allz = true; for (long long z = i; z < i + best; ++z) if (T[z]) { allz = false; break; }
                    if (!allz) bl.push_back(best); i += best; } else ++i; }
            std::sort(bl.rbegin(), bl.rend());
            char b[128]; snprintf(b, sizeof b, " %lld:%lld:%zu:", t, hi - lo + 1, bl.size()); out += b;
            for (size_t z = 0; z < 4 && z < bl.size(); ++z) { snprintf(b, sizeof b, "%s%lld", z ? "/" : "", bl[z]); out += b; }
        }
        printf("%s%s\n", buf, out.c_str()); fflush(stdout);
        for (long long z = lo; z <= hi; ++z) T[z] = 0;
    }
}
