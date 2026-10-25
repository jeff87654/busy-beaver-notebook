// ext: follow 7-state extensions of a base from given start configurations.
//  ext N SLOT < input     SLOT = redirected slot like D1 (its uses = "exhaustions" R)
//  input lines: "M <machine>" sets the machine; "W <name> <tape> <pos> <state>" runs it from that config.
//  output per run: machine world status steps Rhits Gentries ones span lastRstep  [R-hit steps (first 12)] [G entry count per R interval]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
struct TM { int nx[8][2], w[8][2], d[8][2]; int n; };
static void parse(const char *s, TM &m) {
    int q = 0, len = strlen(s);
    for (int i = 0; i < len && q < 8; i += 7) {
        for (int c = 0; c < 2; ++c) {
            const char *x = s + i + 3 * c;
            if (x[0] == '-' || x[2] == 'Z') { m.nx[q][c] = -1; m.w[q][c] = 1; m.d[q][c] = 1; }
            else { m.w[q][c] = x[0] - '0'; m.d[q][c] = x[1] == 'R' ? 1 : -1; m.nx[q][c] = x[2] - 'A'; }
        }
        ++q;
    }
    m.n = q;
}
static std::string rle(const std::vector<unsigned char> &T, long long lo, long long hi, int maxtok) {
    // greedy: at position i find period p in 1..4 maximizing covered length with >=3 reps; else emit literal char
    std::string o; long long i = lo; int tok = 0; std::string lit;
    while (i <= hi && tok < maxtok) {
        long long bestlen = 0; int bp = 0;
        for (int p = 1; p <= 4; ++p) {
            long long j = i + p; while (j <= hi && T[j] == T[j - p]) ++j;
            long long L = j - i; long long reps = L / p;
            if (reps >= 3 && reps * p > bestlen) { bestlen = reps * p; bp = p; }
        }
        if (bp) {
            if (!lit.empty()) { o += lit + " "; lit.clear(); ++tok; }
            std::string u; for (int k = 0; k < bp; ++k) u += char('0' + T[i + k]);
            o += u + "^" + std::to_string(bestlen / bp) + " "; ++tok; i += bestlen;
        } else { lit += char('0' + T[i]); ++i; }
    }
    if (!lit.empty()) o += lit;
    if (i <= hi) o += "...";
    return o;
}
int main(int argc, char **argv) {
    bool DUMP = getenv("EXT_DUMP") != nullptr;
    long long N = atoll(argv[1]);
    int sq = argv[2][0] - 'A', sc = argv[2][1] - '0';
    long long SZ = 1LL << 27; std::vector<unsigned char> T(SZ, 0);
    char cmd[8], a1[256]; static char tape[1 << 20]; TM m; std::string mname;
    while (scanf("%7s", cmd) == 1) {
        if (cmd[0] == 'M') { scanf("%255s", a1); parse(a1, m); mname = a1; continue; }
        long long pos; char st[8];
        scanf("%255s %1048575s %lld %7s", a1, tape, &pos, st);
        long long L = strlen(tape), off = SZ / 2 - L / 2;
        for (long long i = 0; i < L; ++i) T[off + i] = tape[i] - '0';
        long long p = off + pos, lo = off, hi = off + L - 1; int q = st[0] - 'A'; long long t = 0;
        long long R = 0, G = 0, lastR = -1; std::vector<long long> rs; std::vector<long long> gper; long long gcur = 0;
        const char *status = "RUN"; char hb[32];
        while (t < N) {
            int c = T[p];
            if (q == sq && c == sc) { ++R; lastR = t; if (rs.size() < 12) rs.push_back(t); gper.push_back(gcur); gcur = 0; }
            if (m.nx[q][c] < 0) { sprintf(hb, "HALT(%c%d)", 'A' + q, c); status = hb; break; }
            T[p] = m.w[q][c]; p += m.d[q][c]; q = m.nx[q][c]; ++t;
            if (q == 6) { ++G; ++gcur; }
            if (p < lo) lo = p; if (p > hi) hi = p;
            if (p <= 0 || p >= SZ - 1) { status = "OOB"; break; }
        }
        long long ones = 0; for (long long i = lo; i <= hi; ++i) ones += T[i];
        printf("%s\t%s\t%s\t%lld\t%lld\t%lld\t%lld\t%lld\t%lld\t", mname.c_str(), a1, status, t, R, G, ones, hi - lo + 1, lastR);
        for (size_t i = 0; i < rs.size(); ++i) printf("%s%lld", i ? "," : "", rs[i]);
        printf("\t");
        for (size_t i = 0; i < gper.size() && i < 12; ++i) printf("%s%lld", i ? "," : "", gper[i]);
        if (DUMP) { long long a = lo, b = hi; while (a < b && !T[a]) ++a; while (b > a && !T[b]) --b; printf("\t%c@%lld\t%s", (char)(65 + q), p - a, rle(T, a, b, 40).c_str()); }
        printf("\n"); fflush(stdout);
        for (long long i = lo; i <= hi; ++i) T[i] = 0;
    }
}
