// blk: template-free growth probe. Runs a machine from the blank tape for N steps and reports, at the end (and at
// N/10, N/100), the tape span and the longest periodic block (period 1..6) of the tape (in cells), plus halts.
//   blk N < machines.txt   (one machine per line) -> "machine span100 blk100 span10 blk10 span blk status"
#include <cstdio>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>
struct TM { int nx[16][2], w[16][2], d[16][2]; int n; };
static bool parse(const char *s, TM &m) {
    int q = 0, len = strlen(s);
    for (int i = 0; i < len; i += 7) {
        for (int c = 0; c < 2; ++c) {
            const char *x = s + i + 3 * c;
            if (x[0] == '-' || x[2] == 'Z' || (x[2] == 'H' && len < 55)) { m.nx[q][c] = -1; m.w[q][c] = 1; m.d[q][c] = 1; }
            else { m.w[q][c] = x[0] - '0'; m.d[q][c] = x[1] == 'R' ? 1 : -1; m.nx[q][c] = x[2] - 'A'; }
        }
        ++q;
    }
    m.n = q; return q > 0;
}
static long long longest_block(const std::vector<unsigned char> &T, long long lo, long long hi) {
    long long best = 0;
    for (int p = 1; p <= 6; ++p) {
        long long run = 0;
        for (long long i = lo + p; i <= hi; ++i) {
            if (T[i] == T[i - p]) { ++run; if (run + p > best) best = run + p; }
            else run = 0;
        }
    }
    return best;
}
int main(int argc, char **argv) {
    long long N = atoll(argv[1]);
    char buf[256];
    while (scanf("%255s", buf) == 1) {
        TM m; parse(buf, m);
        long long SZ = 1LL << 25;
        std::vector<unsigned char> T(SZ, 0);
        long long p = SZ / 2, lo = p, hi = p;
        int q = 0; long long st;
        std::string rep;
        long long cps[3] = {N / 100, N / 10, N};
        int ci = 0; bool halted = false, tape = false;
        for (st = 0; st < N; ++st) {
            if (st == cps[ci]) { char o[64]; snprintf(o, 64, "%lld %lld ", hi - lo + 1, longest_block(T, lo, hi)); rep += o; ++ci; }
            int c = T[p];
            if (m.nx[q][c] < 0) { halted = true; break; }
            T[p] = m.w[q][c]; p += m.d[q][c]; q = m.nx[q][c];
            if (p < lo) lo = p; if (p > hi) hi = p;
            if (p <= 2 || p >= SZ - 3) { tape = true; break; }
        }
        while (ci < 3) { char o[64]; snprintf(o, 64, "%lld %lld ", hi - lo + 1, longest_block(T, lo, hi)); rep += o; ++ci; }
        printf("%s %s%s\n", buf, rep.c_str(), halted ? "HALT" : tape ? "TAPE" : "RUN");
        fflush(stdout);
    }
    return 0;
}
