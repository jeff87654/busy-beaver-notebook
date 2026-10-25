// gapsnap: run each machine from blank; at checkpoints 1e7,3e7,1e8,3e8 print: span, largest 1-run, number of zero gaps
// >= 8 cells, the 3 largest zero gaps. "machine st | cp: span R1max nbig g1,g2,g3 | ..."
#include <cstdio>
#include <cstring>
#include <vector>
#include <algorithm>
int main() {
    long long cps[4] = {10000000LL, 30000000LL, 100000000LL, 300000000LL}; char line[256];
    std::vector<unsigned char> t(1 << 25);
    while (scanf("%255s", line) == 1) {
        int n = (strlen(line) + 1) / 7, w[16][2], d[16][2], nx[16][2]; bool def[16][2];
        for (int q = 0; q < n; ++q) for (int s = 0; s < 2; ++s) {
            const char *c = line + q * 7 + s * 3;
            def[q][s] = c[0] != '-' && c[2] != '-' && c[2] - 'A' < n;
            if (def[q][s]) { w[q][s] = c[0] - '0'; d[q][s] = c[1] == 'R' ? 1 : -1; nx[q][s] = c[2] - 'A'; }
        }
        std::fill(t.begin(), t.end(), 0); long long p = 1 << 24, lo = p, hi = p; int q = 0; long long i = 0; int ci = 0;
        const char *st = "RUN"; printf("%s", line);
        while (ci < 4) {
            for (; i < cps[ci]; ++i) {
                int s = t[p]; if (!def[q][s]) { st = "HALT"; break; }
                t[p] = w[q][s]; p += d[q][s]; q = nx[q][s];
                if (p < lo) lo = p; if (p > hi) hi = p;
                if (p < 1 || p >= (long long)t.size() - 1) { st = "WIDE"; break; }
            }
            if (st[0] != 'R') break;
            long long a = lo, b = hi; while (a <= b && !t[a]) ++a; while (b >= a && !t[b]) --b;
            long long r1 = 0, cur = 0; std::vector<long long> gaps, runs; long long g = 0;
            for (long long x = a; x <= b; ++x) {
                if (t[x]) { if (g) { gaps.push_back(g); g = 0; } ++cur; r1 = std::max(r1, cur); }
                else { if (cur) runs.push_back(cur); cur = 0; ++g; }
            }
            if (cur) runs.push_back(cur); std::sort(gaps.rbegin(), gaps.rend()); int nb = 0; for (auto v : gaps) if (v >= 8) ++nb;
            std::sort(runs.rbegin(), runs.rend()); int nr = 0; for (auto v : runs) if (v >= 3) ++nr;
            printf(" | %lld %lld %d %lld,%lld,%lld r%d:%lld,%lld,%lld", b - a + 1, r1, nb, gaps.size() > 0 ? gaps[0] : 0, gaps.size() > 1 ? gaps[1] : 0, gaps.size() > 2 ? gaps[2] : 0, nr, runs.size()>0?runs[0]:0, runs.size()>1?runs[1]:0, runs.size()>2?runs[2]:0);
            ++ci;
        }
        printf(" %s %lld\n", st, i); fflush(stdout);
    }
}
