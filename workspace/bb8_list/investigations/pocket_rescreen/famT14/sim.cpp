// sim: literal TM run with RLE snapshots.
// sim MACHINE MIRROR(0/1) STATE WORD HEADPOS NSTEPS EVSTATE MAXEV [mode]
//  WORD: tape string of 0/1 (or '-'), head at index HEADPOS of WORD (may be == len => blank right of word).
//  events: head in EVSTATE on a 0 with no 1 to its right -> print "E step RLE" (RLE of tape from leftmost 1 to head).
//  prints "H step ones" at halt, "END step" at budget.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <cstdint>
struct TM { int nx[16][2], w[16][2], d[16][2]; int ns; };
static bool parse(const char *s, TM &m) {
    std::string x(s); int st = 0, k = 0; size_t i = 0;
    while (i < x.size()) {
        if (x[i] == '_') { ++i; continue; }
        std::string c = x.substr(i, 3); i += 3;
        int sym = k % 2; st = k / 2; ++k;
        if (c[0] == '-') { m.nx[st][sym] = -1; m.w[st][sym] = 1; m.d[st][sym] = 1; continue; }
        m.w[st][sym] = c[0] - '0'; m.d[st][sym] = c[1] == 'R' ? 1 : -1; m.nx[st][sym] = c[2] - 'A';
        if (c[2] == 'Z' ) m.nx[st][sym] = -1;
    }
    m.ns = k / 2; return true;
}
static std::string rle(const std::vector<uint8_t> &T, long long a, long long b) {
    std::string o; long long i = a;
    while (i <= b) { long long j = i; while (j <= b && T[j] == T[i]) ++j; long long L = j - i;
        if (!o.empty()) o += ' ';
        o += char('0' + T[i]); if (L > 1) { o += '^'; o += std::to_string(L); } i = j; }
    return o;
}
int main(int argc, char **argv) {
    if (argc < 9) { fprintf(stderr, "usage\n"); return 2; }
    TM m; parse(argv[1], m); int mir = atoi(argv[2]);
    if (mir) for (int q = 0; q < m.ns; ++q) for (int c = 0; c < 2; ++c) m.d[q][c] = -m.d[q][c];
    int q = argv[3][0] - 'A'; std::string w = strcmp(argv[4], "-") ? argv[4] : "";
    long long hp = atoll(argv[5]), N = atoll(argv[6]); int evq = argv[7][0] == '*' ? -1 : argv[7][0] - 'A'; long long maxev = atoll(argv[8]); long long cnt[16] = {0};
    long long SZ = 2 * N + 2 * (long long)w.size() + 64; if (SZ > (1LL << 30)) SZ = 1LL << 30;
    std::vector<uint8_t> T(SZ, 0);
    long long base = SZ / 2 - (long long)w.size(); long long p = base + hp;
    long long mn = SZ, mx = -1;
    for (size_t i = 0; i < w.size(); ++i) if (w[i] == '1') { T[base + i] = 1; if (base + (long long)i < mn) mn = base + i; if (base + (long long)i > mx) mx = base + i; }
    long long nev = 0;
    for (long long st = 0; st < N; ++st) {
        if (p <= 1 || p >= SZ - 2) { printf("TAPE %lld\n", st); return 0; }
        int c = T[p];
        if (m.nx[q][c] < 0) { long long ones = 0; for (long long i = mn; i <= mx; ++i) ones += T[i]; printf("H %lld %lld | %s\n", st, ones, rle(T, mn < p ? mn : p, mx > p ? mx : p).c_str()); return 0; }
        int wr = m.w[q][c]; T[p] = wr;
        if (wr) { if (p < mn) mn = p; if (p > mx) mx = p; }
        p += m.d[q][c]; q = m.nx[q][c];
        if (evq < 0) {
            if (T[p] == 0) { while (mx >= 0 && mx > p && !T[mx]) --mx; if (mx <= p) cnt[q]++; }
            continue;
        }
        if (q == evq && T[p] == 0) {
            while (mx >= 0 && mx > p && !T[mx]) --mx;
            if (mx > p) continue;
            while (mn < p && !T[mn]) ++mn;
            printf("E %lld %s\n", st + 1, rle(T, mn, p).c_str());
            if (++nev >= maxev) { printf("END %lld ev\n", st + 1); return 0; }
        }
    }
    if (evq < 0) { printf("CNT"); for (int i = 0; i < m.ns; ++i) printf(" %lld", cnt[i]); printf("\n"); }
    printf("END %lld\n", N); return 0;
}
